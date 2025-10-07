import pathlib
import json

path = pathlib.Path(".")

filetypes = ["wav", "ogg", "m4a", "mp3"]
for t in filetypes:
    print('Processing ' + t + ' files')
    for f in path.rglob('*.' + t):
        print(f)
        meta = {'original_path': f.resolve().as_posix()}
        json_object = json.dumps(meta, sort_keys=False, indent=4, ensure_ascii=False)
        with open(f.with_suffix('.json'), "w") as outfile:
            outfile.write(json_object)
    print('Done')




