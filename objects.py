user=dict(
    user_id="",
    full_name="",
    password="",
    email="",
    plans=[], # list of plan_ids - all they have registered for
    current_plans = [], # plan_ids - all plans that are active (plans are removed from each user's current_plans list if the day is not in the active range)
    # future - list of nicknames from all plans
    # future - number of workouts logged
    # future - number of plans completed
    # future - number of unique people with whom you've done plans
)

plans=dict(
    plan_id="",
    name="",
    weeks=dict(), # don't know how to do this? Maybe just do days
    active=0, # boolean
    # nicknames=dict(), # nicknames are plan-dependent, tied to user_id
    messages = dict(), # messages are separate objects
)

day=dict(
    date="datetime",
    binary=0,
)

message=dict(
    text="",
    date_time="datetime",
    plan="",
    person="",
)