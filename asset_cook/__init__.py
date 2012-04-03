import os
import re
import shutil, json
from hashlib import md5

def inject_into_filename(f, s):
    pieces = f.split(".")
    return ".".join(pieces[0: -1]) + s + "." + pieces[-1]

def walk_directory_recursively(path, ext=None):
    if ext != None and not isinstance(ext, list):
        ext = [ext]
    for dirname, directories, file_names in os.walk(path, followlinks=True):
        dirname = dirname.replace("\\", "/")
        print directories
        for file_name in file_names:
            if ext == None or file_name.split(".")[-1] in ext:
                yield (dirname + "/" + file_name, file_name)

def create_assets_dictionary(path):
    assets_dict = {}
    for asset in walk_directory_recursively(path, ["jpg", "png", "gif", "jpeg", "swf", "ttf"]):
        asset_id = asset[0][1 + len(path):]
        if asset_id.find("-XproductionX-") >= 0:
            continue
        md5hasher = md5()
        f = open(asset[0], "r")
        content = f.read()
        f.close()
        md5hasher.update(content)
        hash_val = md5hasher.hexdigest()
        assets_dict[asset_id] = inject_into_filename(asset_id, "-XproductionX-" + hash_val)
        shutil.copy2(asset[0], inject_into_filename(asset[0], "-XproductionX-" + hash_val))
    return assets_dict
        
def search_and_destroy(file_content, path, regexp, tag, end_tag, template_name, proc, proc_params):
    index = 0
    prev_match = 0
    js_group = []
    global_js = []
    for match in re.finditer(regexp, file_content):
        match_start = match.start()
        js_file = file_content[match.start(1) : match.end(1)]
        delimiters_count = file_content[prev_match : match_start].count("\n")
        if delimiters_count > 1 and prev_match > 0:
            index += 1
            global_js.append((proc(path, [js[0] for js in js_group], template_name, index, **proc_params), js_group[0][1], js_group[-1][2]))
            js_group = []
        js_group.append((js_file, match_start, match.end()))
        prev_match = match_start
    if js_group:
        index += 1
        global_js.append((proc(path, [js[0] for js in js_group], template_name, index, **proc_params), js_group[0][1], js_group[-1][2]))
    template_copy = ""
    cur_index = 0
    if global_js:
        for js in global_js:
            template_copy += file_content[cur_index : js[1]] + tag + js[0] + end_tag#
            cur_index = js[2]
        template_copy += file_content[js[2]:]  
        return template_copy
    else:
        return file_content
            
def process_templates(templates_path, static_path):
    js_path = static_path + "/js/"
    css_path = static_path + "/css/"
    assets = create_assets_dictionary(static_path)
    for template_file_name, short_name in walk_directory_recursively(templates_path, "html"):
        f = open(template_file_name, "r")
        file_content = f.read()
        f.close()
        template_copy = search_and_destroy(file_content, js_path, r'<script src="{{ STATIC_URL }}js/([/.0-9A-Za-z_-]+\.js)"></script>', "<script src='", "'></script>", short_name, compile_js_group, {})
        template_copy = search_and_destroy(template_copy, css_path, r'<link rel="stylesheet" type="text/css" href="{{ STATIC_URL }}css/([/.0-9A-Za-z_-]+\.css)"/>', "<link rel='stylesheet' type='text/css' href='", "'/>", short_name, compile_css_group, {'assets': assets})
        head_start = template_copy.index("<head>")
        assets_string = "\t\n<script>var ASSETS = " + json.dumps(assets) + ";</script>"
        f = open(template_file_name + ".fixed", "w")
        f.write(template_copy[0 : head_start + 6] + assets_string + template_copy[head_start + 6 :])
        f.close()

def compile_css_group(css_path, css_group, template, index, assets):
    css_files = []
    for css in css_group:
        f = open(css_path + css, "r")
        css_files.append(f.read())
        f.close()
    content = "\n\n".join(css_files)
    replaces = []
    for match in re.finditer(r'url\((.+?)\)', content):
        bad_id = content[match.start(1) : match.end(1)].strip('\' ./')
        replaces.append((match.start(1), match.end(1), "'../" + assets[bad_id] + "'"))
    if replaces:
        new_content = ''
        cur_index = 0
        for replace in replaces:
            new_content += content[cur_index : replace[0]] + replace[2]
            cur_index = replace[1]
        new_content += content[replace[1] : ]
        content = new_content
    hasher = md5()
    hasher.update(content)
    hash_val = hasher.hexdigest()
    file_name = template + "-" + str(index) + hash_val + ".css"
    f = open(css_path + file_name, "w")
    f.write(content)
    f.close()
    return "{{ STATIC_URL}}css/" + file_name
       
def compile_js_group(js_path, js_group, template, index):
    if not js_group:
        return
    free_js = []
    module_js = []
    discovered_set = {js for js in js_group}
    counter = 0
    while len(js_group) > counter:
        js = js_group[counter]
        js_file_handle = open(js_path + js, "r")
        js_file = js_file_handle.read()
        js_file_handle.close()
        match = re.match(r"new Module\('.+', \[(.*)\]", js_file)
        if match:
            dependencies = [piece.strip(" '\"") for piece in match.group(1).split(",") if len(piece) > 0]
            for p in dependencies:
                if not p in discovered_set:
                    discovered_set.add(p)
                    js_group.append(p)
            module_js.append([js, dependencies])
        else:
            free_js.append(js_file)
        counter += 1
    modules = {js[0]: {dep for dep in js[1]} for js in module_js}
    ordered_modules = []
    while len(modules.keys()) > 0:
        to_remove = []
        for module, deps in modules.iteritems():
            if len(deps) == 0:
                ordered_modules.append(module)
                for d in modules.values():
                    if module in d:
                        d.remove(module)
                to_remove.append(module)
        for el in to_remove:
            del modules[el]
    for module in ordered_modules:
        handle = open(js_path + module, "r")
        module_content = handle.read()
        pieces = module_content.split("\n")[1:]
        while pieces[-1].strip(" \t") != "})":
            pieces.pop()
        pieces.pop()
        free_js.append("\n".join(pieces))
        handle.close()
    total_js = "\n\n".join(free_js)
    md5hasher = md5()
    md5hasher.update(total_js)
    hash_val = md5hasher.hexdigest()
    short_name = template + "-" + str(index) + "-" + hash_val + ".js"
    f = open(js_path + short_name, "w")
    f.write(total_js)
    f.close()
    return "{{ STATIC_URL }}js/" + short_name
