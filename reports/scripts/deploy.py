import argparse
import json
import os
import re

import nbformat
from traitlets.config import Config
from nbconvert import HTMLExporter

from playwright.sync_api import sync_playwright
from PIL import Image


def get_nodebook_info(notebook):
    """ find the code cell that has the METADATA variable defined and return it
        as a python object """
    for cell in notebook.cells:
        if cell['cell_type'] == 'code' and cell['source'].startswith("METADATA = "):
            return eval(cell['source'][len("METADATA = "):])

    return None

def resize_thumbnail(filename):
    img = Image.open(filename)

    width = 150
    height = int(float(img.size[1]) * float(width) / float(img.size[0]))

    img = img.resize((width, height), Image.Resampling.LANCZOS)
    img.save(filename)

def process_notebook(filename, outdir):
    """ open a notebook file and check if it has a cell with METADATA variable defined
        if so then export the notebook to html and return the report information for use
        with XDMoD custom report tab """

    report_id = None
    report_meta = None

    with open(filename, "r") as filep:
        notebook = nbformat.read(filep, as_version=4)
        
        md = get_nodebook_info(notebook)
        if md:
            out_file =  f"{os.path.basename(filename[:-6])}_v{md['version']}.html"

            report_id = re.sub(r"[^\w]", "_", md['title'].lower())
            report_meta = {
                'thumbnail': f'{report_id}-thumbnail.png',
                'title': md['title'],
                'version': md['version'],
                'description': md['description'],
                'filename': out_file
            }
            
            c = Config()
            c.TemplateExporter.exclude_input_prompt = True
            c.TemplateExporter.exclude_output_prompt = True
            c.TemplateExporter.exclude_input = True

            html_exporter = HTMLExporter(config=c, template_name="lab")
            (body, resources) = html_exporter.from_notebook_node(notebook)

            html_filename = os.path.abspath(os.path.join(outdir, out_file))
            with open(html_filename, "w") as outp:
                outp.write(body)

            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page()
                page.goto(f'file://{html_filename}#thumbnail')
                page.wait_for_load_state()
                page.screenshot(path=os.path.join(outdir, report_meta['thumbnail']))
                browser.close()
            
            resize_thumbnail(os.path.join(outdir, report_meta['thumbnail']))

    return (report_id, report_meta)


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('filename', nargs='+')
    parser.add_argument('-o', '--outdir', help='The directory to write html reports and the XDMoD config file.')
    args = parser.parse_args()

    data = {}
    for file in args.filename:
        if not file.endswith(".ipynb"):
            continue

        (report_id, report_meta) = process_notebook(file, args.outdir)
        if report_id:
            data[report_id] = report_meta
            
    with open(os.path.join(args.outdir, 'custom_reports.json'), "w") as outp:
        json.dump(data, outp, indent=4)


if __name__ == "__main__":
    main()

