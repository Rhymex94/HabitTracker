# Habit Tracker

Monorepo for both the backend and frontend of the habit tracker app.

TODOs:

Feature todos:
-   Implement a stats view of habits:
    -   Percentage of completed days/weeks/months/years
-   Implement "units" (for quantitative habits. Minutes, repetitions etc.)
    -   Model field added. Implement changes to the UI and the API
-   Add a checkbox to control whether the user wants to add a custom target value (not 1)
-   Display server-side validation errors in the UI

Technical todos:
-   Consider combining the Habit modals, or to use the same root file
-   Change the add-button, save-button and add-progress classes to use the button-primary
    class instead.
-   Make sense of the tests. Consider using Factories. Clean mocks/fixtures
    -   Use fixtures for the User/Authentication setup to not have to worry about it
    -   Use parametrization for helper functions to test edge-cases
    -   Use mocks for nested helper function calls (already testing individual helpers)
    -   Use factories for setting up DB data for actual endpoint tests
-   Move the VITE_API_URL away from the build args (requires runtime injection of env vars)