# noinspection PyUnresolvedReferences
from h2o_wave import Q, main, app, ui

CURRENCIES = ['RON', 'EUR']


@app('/')
async def serve(q: Q):
    q.page['form'] = ui.form_card(
        box='4 1 6 12',
        items=[
            ui.file_upload(name='file_upload', label='File Upload'),
            ui.inline(items=[
                ui.combobox(name='type', label='Type', choices=['Withdrawal', 'Deposit', 'Transfer'], width='25%',
                            required=True),
                ui.textbox(name='description', label='Description', value='', width='75%', required=True),
            ]),
            ui.inline(items=[
                ui.combobox(name='source_account', label='Source Account',
                            choices=['Cyan', 'Magenta', 'magunta', 'Yellow', 'Black'], width='50%', required=True),
                ui.combobox(name='destination_account', label='Destination Account',
                            choices=['Cyan', 'Magenta', 'magunta', 'Yellow', 'Black'], width='50%', required=True),
            ]),
            ui.inline(items=[
                ui.date_picker(name='date', label='Date', width="50%", ),
                ui.combobox(name='category_name', label='Category Name',
                            choices=['Cyan', 'Magenta', 'magunta', 'Yellow', 'Black'], width="50%")
            ]),
            ui.inline(items=[
                ui.textbox(name='amount', label='Amount', width="50%", mask='99.99', required=True),
                ui.combobox(name='currency_code', label='Currency',
                            choices=CURRENCIES, width="50%", value=CURRENCIES[0])
            ]),
            ui.inline(items=[
                ui.textbox(name='foreign_amount', label='Foreign Amount', width="50%", mask='99.99', required=True),
                ui.combobox(name='foreign_currency_code', label='Foreign Currency',
                            choices=CURRENCIES, width="50%")
            ]),
            ui.textbox(name='notes', label='notes', width="100%", multiline=True, value="asd\n" * 100),
            ui.buttons(justify='center', items=[
                ui.button(name='submit_button', label='Submit', width='100%', primary=True)
            ])

        ])
    await q.page.save()
