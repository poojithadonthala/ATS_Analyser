
## If ATS analysis returns 401

The ATS analyze and result endpoints require the currently signed-in user's bearer token. Sign out and sign in again to refresh the browser session, then retry from the application’s Resume page. Confirm the backend is running at the configured API origin (`VITE_API_URL`, default `http://localhost:8000`). Calling the protected endpoint directly in a browser address bar will return 401 because it does not include the bearer token; use the authenticated HireX screen or an API client with an Authorization header.
