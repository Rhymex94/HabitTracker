# Habit Tracker

Monorepo for both the backend and frontend of the habit tracker app.

TODOs:

-   Consider combining the Habit modals, or to use the same root file
-   Implement a stats view of habits:
    -   Percentage of completed days/weeks/months/years
    -   Display the current streak (and perhaps max streak?)
-   Change the add-button, save-button and add-progress classes to use the button-primary
    class instead.
-   Implement "units" (for quantitative habits. Minutes, repetitions etc.)
-   Limit the amount of entries fetched by the UI. Won't need entire history every time.
-   Hide target_value from Habits that are BINARY (only 1 makes sense with these).
-   Make sense of the tests. Consider using Factories. Clean mocks/fixtures
    -   Use fixtures for the User/Authentication setup to not have to worry about it
    -   Use parametrization for helper functions to test edge-cases
    -   Use mocks for nested helper function calls (already testing individual helpers)
    -   Use factories for setting up DB data for actual endpoint tests