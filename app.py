from flask import Flask, render_template, flash, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'

class InputForm(FlaskForm):
    input_type_id = IntegerField('Input Type ID', validators=[DataRequired()])
    input_quantity = IntegerField('Input Quantity', validators=[DataRequired()])
    output_type_id = IntegerField('Output Type ID', validators=[DataRequired()])
    output_quantity = IntegerField('Output Quantity', validators=[DataRequired()])
    region = StringField('Region', validators=[DataRequired()])
    submit = SubmitField('Calculate')

@app.route('/', methods=['GET', 'POST'])
def calculator():
    form = InputForm()
    if form.validate_on_submit():
        input_type_id = form.input_type_id.data
        input_quantity = form.input_quantity.data
        output_type_id = form.output_type_id.data
        output_quantity = form.output_quantity.data
        region = form.region.data

        # Retrieve market data using EVE ESI API
        access_token = "" # Enter your EVE Online ESI API access token here
        headers = {'Authorization': f'Bearer {access_token}'}
        input_market_data = requests.get(f'https://esi.evetech.net/latest/markets/{region}/orders/?datasource=tranquility&order_type=all&page=1&type_id={input_type_id}', headers=headers).json()
        output_market_data = requests.get(f'https://esi.evetech.net/latest/markets/{region}/orders/?datasource=tranquility&order_type=all&page=1&type_id={output_type_id}', headers=headers).json()

        # Calculate total cost, total revenue, and profit margin
        input_cost = sum(order['price'] * order['volume_remain'] for order in input_market_data if order['is_buy_order']) / input_quantity
        output_revenue = sum(order['price'] * order['volume_remain'] for order in output_market_data if not order['is_buy_order']) / output_quantity
        total_cost = input_cost * input_quantity
        total_revenue = output_revenue * output_quantity
        profit_margin = (total_revenue - total_cost) / total_revenue * 100

        # Display results
        flash(f'Total Cost: {total_cost:,.2f} ISK')
        flash(f'Total Revenue: {total_revenue:,.2f} ISK')
        flash(f'Profit Margin: {profit_margin:.2f}%')
        return redirect(url_for('calculator'))
    return render_template('calculator.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
