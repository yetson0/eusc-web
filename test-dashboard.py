import panel as pn
pn.extension(template='fast') # for notebook

# build interactive slider
def star_creator(number):
  return "⭐" * number
slider = pn.widgets.IntSlider(name='Stars', value=5, start=1, end=10)
interactive_star_creator = pn.bind(star_creator, slider)

text_input = pn.widgets.TextInput(name='Text') # more widgets
def text_creator(text):
  return f'{text}'
interactive_text_creator = pn.bind(text_creator, text_input)

# build components by Row or Column
# row = pn.Row('Slider', w1, slider, interactive_star_creator)
# row

column = pn.Column('# Eusc', text_input, slider, interactive_star_creator)
# column.append(f'# H1 section \n sometext: {text_input.value}')
column.append(interactive_text_creator)
column.servable(target='pyscript_app')