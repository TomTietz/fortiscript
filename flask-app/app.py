# app.py
from flask import Flask, render_template, request
import utility.transform as t
from jinja2 import Template
import utility.jinja as j
import json

app = Flask(__name__)
@app.route('/')
def home():
    return render_template('home.html')


@app.route('/csv-to-cli', methods=['GET', 'POST'])
def csv_to_cli():
    output_text = ''
    selected_separator = ';'
    naming = 'vlan_'
    format_names = False
    delete_obj = False
    error = None
    if request.method == 'POST':
        try:
            delete_obj = 'delete_obj' in request.form  # Check if delete_obj switch is on
            format_names = 'format_names' in request.form  # Check if format_names switch is on
            vlan_data_text = request.form.get('input_text1', '')
            route_data_text = request.form.get('input_text2', '')
            naming = request.form.get('naming', 'vlan_')
            selected_separator = request.form.get('separator', ',')
            actual_separator = ';'
            if selected_separator == 'excel':
                vlan_data_text = t.excel_to_csv(vlan_data_text)
                route_data_text = t.excel_to_csv(route_data_text)
            else:
                actual_separator = selected_separator

            vdom = request.form.get('vdom', '').strip()
            if not vdom:
                vdom = None
            
            # TODO: Error handling
            if 'vlan_button' in request.form:
                output_text, vlans = t.script_vlans(vlan_data_text,vdom=vdom,delimeter=actual_separator,naming=naming,format_names=format_names)
                output_text += t.script_zones(vlan_data_text,vdom=vdom,delimeter=actual_separator,naming=naming,format_names=format_names)
                if delete_obj:
                    output_text += t.script_address_object_removal(vlans)   
            elif 'route_button' in request.form:
                output_text = t.script_routes(route_data_text,vdom=vdom,delimeter=actual_separator)
        except Exception as e:
            if isinstance(e, KeyError):
                error = f"Input error: CSV keys not found. Ensure you are using the correct delimeter."
            else:
                error = f"Input error: {str(e)}"
    return render_template('csv-to-cli.html',
                        error=error,
                        output_text=output_text,
                        selected_separator=selected_separator,
                        delete_obj=delete_obj,
                        selected_naming=naming,
                        format_names=format_names,
                        show_warning=(selected_separator == 'excel'))


@app.route('/templates')
def templates():
    return render_template('templates.html')

@app.route('/address', methods=['GET', 'POST'])
def address():
    output_text = ''
    error = ''
    selected_separator = ';'
    ipversion = '4'
    if request.method == 'POST':
        try:
            data_text = request.form.get('input_text1', '')
            ipversion = request.form.get('ipversion', ',')
            selected_separator = request.form.get('separator', ',')
            actual_separator = ';'
            if selected_separator == 'excel':
                data_text = t.excel_to_csv(data_text)
            else:
                actual_separator = selected_separator

            vdom = request.form.get('vdom', '').strip()
            if not vdom:
                vdom = None
            
            if 'addr_button' in request.form:
                output_text = t.script_addresses(data_text,vdom=vdom,delimeter=actual_separator,ipversion=int(ipversion))
            
        except Exception as e:
            error = f"Input error: {str(e)}"

    return render_template('address.html', 
                         error=error,
                         output_text=output_text,
                         selected_separator=selected_separator,
                         show_warning=(selected_separator == 'excel'))


@app.route('/jinja', methods=['GET', 'POST'])
def jinja():
    output = ''
    error = ''
    template_content = ''
    variables_content = ''
    
    if request.method == 'POST':
        try:
            template_content = request.form.get('template', '')
            variables_content = request.form.get('variables', '{}')
            
            # Parse variables
            context = json.loads(variables_content)
            
            # Render template
            template = Template(template_content)
            output = template.render(context)
            
        except json.JSONDecodeError:
            error = "Invalid JSON format in variables"
        except Exception as e:
            error = f"Template error: {str(e)}"

    return render_template('jinja.html', 
                         output=output,
                         error=error,
                         template_content=template_content,
                         variables_content=variables_content)


@app.route('/converter', methods=['GET', 'POST'])
def converter():
    output_text = ''
    error = ''
    selected_vendor = ';'
    ipversion = '4'
    if request.method == 'POST':
        try:
            vlan_text = request.form.get('input_text1', '')
            route_text = request.form.get('input_text2', '')
            selected_vendor = request.form.get('vendor', ',')

            vdom = request.form.get('vdom', '').strip()
            if not vdom:
                vdom = None
            
            if 'convert_button' in request.form:
                output_text = vlan_text.upper()+route_text.upper()
            
        except Exception as e:
            error = f"Input error: {str(e)}"

    return render_template('address.html', 
                         error=error,
                         output_text=output_text,
                         selected_vendor=selected_vendor)


@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)