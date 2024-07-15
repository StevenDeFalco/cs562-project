# ExtendedSQL Interface

This document contains information about the ExtendedSQL interaface. It will provide instrructions on all features of the ExtendedSQL application.

This documentation is intended to help users naviagate the interface and allows for the intended usage of each feature.


## Table of Contents


## Query Panel

When the application starts up, the central area of the window will show the ExtendedSQL logo. This space will eventually be where you can write and execute ESQL queries.

### Query Tabs

The `New Query` button is located to the top left of the main window. When clicked, it will create a new tab with text editing capabilities. It will also open the output panel, which will show the output of an executed query.

Tabs can be deleted by clicking the `x` icon to the right of the tab name. By default, tabs will be named `Query #`, where `#` starts with `1` and continues to increment as long as the application is running and new tabs are being opened. 

On the menu panel at the top of the screen, under `File`, there is the option to `Save` and the option to `Open`. These options are also present on the output panel.

`Save` allows for the query on the current query tab to be renamed and saved. ESQL queries should be saved as a `.esql` or `.txt` file.

`Open` allows for a file saved on the local machine to be opened in a new query tab. This tab will have the name of the file that was opened.

### Output Screen

The output screen will be open whenever a query tab is open. The screen will show the output of a query execution.

To execute a query, navigate to the menu panel and click `Execute` under `Run`. You can also click `Execute` on the top right of the output panel.

If the query has a parsing error, this will show on the screen along with an error message. This message should help direct you towards writing a proper ESQL query. If you are stuck trying to write an executable query, refer to [documentation](syntax.md) on ExtendedSQL queries.

When a query can be parsed and executes, there resulting table will be displayed on the output screen.

### Text Editor Options

...



## Table Panel

### New Table

