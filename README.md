# Septic API!


## Running the app.

1. git clone https://github.com/bdauer/septic_api
1. From the repository's root, create and activate a virtual environment.
2. `pip install -r requirements.txt`
3. `python3 manage.py migrate`
3. `python3 manage.py runserver`
4. Go to `http://127.0.0.1:8000/home/unregistered_home_data/?zip=02845&address=123dsaljkdsa&fields=has_septic` in your browser.


## General Considerations

This section of the README covers general considerations. For specific considerations see comments in the code.

* Flask would have been a better framework for a small project. I chose Django and DRF since it's your stack.

* I should have asked for clarification about why the data would
be retrieved from a different API than House Canary. I didn't think through where that would be declared.
Cases to consider:
  * different endpoint accessed based on type of data submitted, 
  * combined data from multiple endpoints,
  * secondary endpoint if the initial endpoint fails.

* There are multiple House Canary endpoints for different types of data. 
The web service could split into different flows for different endpoints.

* I haven't added any logging. In a real world scenario I'd want to log exceptions with helpful information.

* It would be better to catch exceptions, and deal with bad http responses, in the service.
The service could consistently have the same exception for similar problems from different endpoints.

* I haven't added any tests. I'd want to create unit tests covering the different edge cases.
It would be good to have an integration or functional test to make sure that the whole system works together.

* The swagger setup only tests the happy path. I haven't tested that all of the edge case logic works as intended.

* I disabled all auth. This data isn't very sensitive but in a real world scenario I'd want
some authorization.