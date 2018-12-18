import numpy as np
import plotly.plotly as py
import plotly.graph_objs as go
import plotly.figure_factory as ff
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import pandas as pd
from datetime import datetime
import pymongo
from flask_pymongo import PyMongo
from validate_email import validate_email
import shortuuid
from flask import Flask

server = Flask(__name__)

app = dash.Dash(
    __name__,
    server = server,
    external_stylesheets=["https://codepen.io/chriddyp/pen/bWLwgP.css"]
)
app.scripts.config.serve_locally = True
app.title="FitFam"
app.config.requests_pathname_prefix = '' 


uri = "mongodb://localhost:27017"
mongo = PyMongo(server,uri)
db = mongo.cx.fitfam


tab_selected_style=dict(backgroundColor="lightBlue")

app.layout=html.Div(
        children = [
            html.Div( # header
                id='header-div',
                style=dict(width="100%",height="5%",textAlign='center',fontSize='5vmin',backgroundColor="darkGrey",color="white",fontWeight='bold'),
                children=[
                    "FitFam",
                    dcc.Store(
                        id='session-store',
                        storage_type='session'
                    ),
                    dcc.Store(
                        id='local-store',
                        storage_type='local'
                    )
                ]
            ),
            html.Div(
                id='identity-div',
                style=dict(textAlign="center",margin='auto',width="100%"),
                # try pulling from the brower store first; if that doesn't work, ask who they are 
                children=[
                    dcc.Input(
                        id='i-am-email-input',
                        style=dict(width="100%",height="7vmin",fontSize='5vmin',),
                        placeholder="user email",
                    ),
                    dcc.Input(
                        id='i-am-password-input',
                        style=dict(width="100%",height="7vmin",fontSize="5vmin",),
                        placeholder="user password",
                    ),
                    dcc.Checklist(
                        id='store-identity-checkbox',
                        options=[dict(label="Remember me",value=1)],
                        values=[1],
                        style=dict(margin='auto',width="100%",display='inline-block'),
                        labelStyle=dict(fontSize="5vmin"),
                        inputStyle=dict(height="5vmin",width="5vmin")
                    ),
                    html.Button(
                        id="i-am-submit-button",
                        children='submit',
                        n_clicks=0,
                        style=dict(color='white',backgroundColor="navy",fontWeight="bold",fontSize="5vmin",height="100%",width="100%",lineHeight="normal",whiteSpace="normal"),
                    ),
                    html.Button(
                        id='i-am-new-here-button',
                        n_clicks=0,
                        style=dict(color='white',background="forestGreen",fontWeight="bold",fontSize="5vmin",height="100%",width="100%",lineHeight="normal",whiteSpace="normal",),
                        children="I don't have an account!"
                    ),                       
                ]
            ),
            html.Div(
                id='user-reg-div-wrapper',
                style=dict(display='none'),
                children=[
                    html.Div(
                        id='user-reg-div',
                        style=dict(),
                        children=[
                            html.Div("Enter info, submit, and then login.",style=dict(width="100%",fontSize="5vmin")),
                            dcc.Input(
                                id='user-reg-name-input',
                                placeholder="Full name",
                                style=dict(width="100%",fontSize="5vmin")
                            ),
                            html.Div("",id='user-reg-output-div-name'),
                            dcc.Input(
                                id='user-reg-email-input',
                                placeholder="Email",
                                style=dict(width="100%",fontSize="5vmin")
                            ),
                            html.Div("",id='user-reg-output-div-email'),
                            dcc.Input(
                                id='user-reg-password-input',
                                placeholder="Password",
                                style=dict(width="100%",fontSize="5vmin")
                            ),
                            dcc.Input(
                                id='user-reg-password-confirm-input',
                                placeholder="Confirm Password",
                                style=dict(width="100%",fontSize="5vmin")
                            ),
                            html.Div("",id='user-reg-output-div-password'),
                            dcc.ConfirmDialogProvider(
                                id='user-reg-confirm-dialog',
                                submit_n_clicks=0,
                                message="Are you sure this registration info is correct? Click OK if you're sure.",
                                children=[
                                    html.Button(
                                        id='user-reg-submit-button',
                                        n_clicks=0,
                                        children="Submit Registration",
                                        style=dict(color='white',background="purple",fontWeight="bold",fontSize="5vmin",height="100%",width="100%",lineHeight="normal",whiteSpace="normal",),
                                    ),
                                ]
                            )
                       ]
                    ),
                ]
            ),
            html.Div([
                html.Div(),
                dcc.Tabs(
                    id='tabs',
                    children=[
                        html.Div(
                            id='tabs-div',
                            style=dict(display="none"),
                            children=[
                                dcc.Tab(
                                    id='me-tab',
                                    style=dict(width="100%"),
                                    label="Me",
                                    children=html.Div(
                                        id="me-div",
                                        style=dict(height="90%",width="100%"),
                                        children=[
                                            html.H2(id='me-header',children="Me Tab"), # show name of person
                                            html.Div(
                                                id='me-div-main',
                                                style=dict(),
                                                children=[
                                                    html.Div(
                                                        id='last-seven-days',
                                                        style=dict(),
                                                        children="", # track clicks with abs(x-1) where x is current T/F value
                                                    )
                                                ]
                                            )
                                        ]
                                    )
                                ),
                                dcc.Tab(
                                    id='plan-tab',
                                    style=dict(height="90%",width="100%"),
                                    label="Plans",
                                    children=[
                                        html.Div(
                                            id="plans-div",
                                            style=dict(),
                                            children=[
                                                html.H1("Plans Tab")
                                            ]
                                        )
                                    ]
                                )
                            ]
                        )
                    ]
                )
            ]) 
    ]
)



# check login info
@app.callback(
    Output('identity-div','style'),
    [Input('i-am-submit-button','n_clicks')],
    [State('i-am-email-input','value'),
     State('i-am-password-input','value'),
     ])
def user_login(clicks,email,password):
    
    # data=data or {}
    # if data=={}:
    #     raise PreventUpdate
    # if db.users.find_one(dict(email=data['email']))['password'] == password:
    #         return dict(display="none")
    if not clicks:
        return dict(textAlign="center",margin='auto',width="100%")
    # check to see if email is in the db and if it matches
    if db.users.find_one(dict(email=email))["password"] == password:
        return dict(display='none')
# store user data locally
@app.callback(
    Output('local-store','data'),
    [Input('i-am-submit-button',"n_clicks")],
    [State('i-am-email-input','value'),
     State('i-am-password-input','value'),
     State('store-identity-checkbox',"values")])
def store_local(n_clicks,email,password,keep):
    if not n_clicks: 
        return ""
    if not keep:
        return ""
    return {"email":email,"password":password}
@app.callback(
    Output('session-store','data'),
    [Input('i-am-submit-button',"n_clicks")],
    [State('i-am-email-input','value'),
     State('i-am-password-input','value')])
def store_session(n_clicks,email,password):
    if not n_clicks:
        return ""
    return dict(email=email,password=password)
# shows user registration
@app.callback(
    Output('user-reg-div-wrapper','style'),
    [Input('i-am-new-here-button','n_clicks')],)
def show_user_reg_div(n_clicks):
    if n_clicks%2==0:
        return dict(display='none')
    return dict()
# submit user registration
@app.callback(
    Output('user-reg-div','style'),
    [Input('user-reg-confirm-dialog','submit_n_clicks')],
    [State('user-reg-name-input','value'),
     State('user-reg-email-input','value'),
     State('user-reg-password-input','value')])
def submit_user_registration(n_clicks,name,email,password):
    if n_clicks==0:
        return dict()
    # submit the things to database
    user_dict = dict(
        user_id=shortuuid.uuid(),
        full_name=name,
        password=password,
        email=email,
        plans=[], # list of plan_ids - all they have registered for
        current_plans=[], # plan_ids - all plans that are active (plans are removed from each user's current_plans list if the day is not in the active range)
    )
    db.users.insert_one(user_dict)
    dict(display="none")
# actively check if passwords match
@app.callback(
    Output('user-reg-output-div-password','children'),
    [Input('user-reg-password-input','value'),
     Input('user-reg-password-confirm-input','value')],
     [State('i-am-new-here-button','n_clicks')])
def check_password_match(pass1,pass2,n):
    if not n:
        return ""
    if pass1=="" and pass2=="":
        return ""
    if pass1==pass2:
        return ""
    return html.Div("Passwords do not match ⛔️",style=dict(width="100%",fontSize="5vmin"))
# actively check if email exists
@app.callback(
    Output('user-reg-output-div-email','children'),
    [Input('user-reg-email-input','value')],
    [State('i-am-new-here-button','n_clicks')])
def check_email(email,n):
    if not n:
        return ""
    if email=="":
        return ""
    if not validate_email(email):
        return html.Div("Invalid email ⛔️",style=dict(width="100%",fontSize="5vmin"))
    if db.users.find_one(dict(email=email)):
        return html.Div("Email already exists 🙀",style=dict(width="100%",fontSize="5vmin"))
    return 
# check if name is ""
@app.callback(
    Output('user-reg-output-div-name','children'),
    [Input('user-reg-name-input','value')],
    [State('user-reg-password-input','value'),
     State('user-reg-email-input','value'),
     State('i-am-new-here-button','n_clicks')])
def check_name(name,password,email,n):
    if not n:
        return ""
    if name=="" and password=="" and email=="":
        return ""
    if name=="":
        return html.Div("You have to have a name! 😳",style=dict(width="100%",fontSize="5vmin"))

@app.callback(
    Output('tabs-div','style'),
    [Input('identity-div','style')])
def show_me_div(s):
    if s==dict(display='none'):
        return dict(width="100%",textAlign='center',fontSize='5vmin',display='block',verticalAlign='bottom')
#@app.callback(
#    Output('identity-div','style'),
#    [Input('i-am-new-here-button','n_clicks')])
#def hide_identity_div(n_clicks):
#    return dict(display="none")
#@app.callback()
#def return_person_name():
#    return ""
#@app.callback()
#ef return_plans():
#    return ""



@server.route('/')
def myDashApp():
    return app

if __name__ == '__main__':
    app.run_server(
        debug=True, 
        threaded=True,
        port=5000
    )