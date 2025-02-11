# ExtendedSQL Interface

This document contains information about the ExtendedSQL interaface. It will provide instrructions on all features of the ExtendedSQL application.

This documentation is intended to help users naviagate the interface and allows for the intended usage of each feature.


## Table of Contents
- [Query Panel](#query-panel)
    - [Query Tabs](#query-tabs)
    - [Output Screen](#output-screen)
    - [Text Editor Options](#text-editor-options)
- [Table Panel](#table-panel)
    - [Tables](#tables)
    - [New Table](#new-table)


## Query Panel

When the application starts up, the central area of the window will show the ExtendedSQL logo. This space will eventually be where you can write and execute ESQL queries.

### Query Tabs

The `New Query` button is located to the top left of the main window. When clicked, it will create a new tab with text editing capabilities. It will also open the output panel, which will show the output of an executed query.

Tabs can be deleted by clicking the `x` icon to the right of the tab name. By default, tabs will be named `Query #`, where `#` starts with `1` and continues to increment as long as the application is running and new tabs are being opened. 

On the menu panel at the top of the screen, under `File`, there is the option to `Save` and the option to `Open`. These options are also present on the output panel.

`Save` allows for the query on the current query tab to be renamed and saved. ESQL queries should be saved as a `.esql` or `.txt` file.

`Open` allows for a file saved on the local machine to be opened in a new query tab. This tab will have the name of the file that was opened.

### Output Screen

The output screen will be open whenever a query tab is open. The screen can be moved vertically to allow for more space to either to view the output or the query that is being written. The screen will show the output of a query execution.

To execute a query, navigate to the menu panel and click `Execute` under `Run`. You can also click `Execute` on the top right of the output panel.

If the query has a parsing error, this will show on the screen along with an error message. This message should help direct you towards writing a proper ESQL query. If you are stuck trying to write an executable query, refer to [documentation](syntax.md) on ExtendedSQL queries.

When a query can be parsed and executes, there resulting table will be displayed on the output screen.

### Text Editor Options

Common text editor functionality are accessible for the text editor on the query tabs. These include:

- Undo (`Ctrl Z`)
- Redo (`Ctrl Y`)
- Copy (`Ctrl C`)
- Paste (`Ctrl V`)
- Zoom In (`Ctrl +`)
- Zoom Out (`Ctrl -`)

These options cannot be used outside of the query tab text editor.


## Table Panel

The table panel to the left of the window displays all of the tables that have been imported into the project. Table information is stored in `.tables`, so leave this directory alone.

### Tables

Each table that is improted into the project is loaded from `.tables` upon execution of ExtendedSQL. To delete a table, right click on the name of the table and select `Delete`. This will remove the table from the panel and the `.tables` directory. `Get Info` currently does not do anything.

### New Table

To create a new table, click the `New Table` button to the top left of the window and above the table panel. 

Currently the only way to add a table in ExtendedSQL is to import it from PostgreSQL. Therefore, you want to first ensure that there is a table in PostgreSQL that you want to import into ExtendedSQL.

Then, input the `table name` along with the `username`, `password`, `port number`, and `host name`. The default values can usually be left as __localhost__ for `host name` and __5432__ for `port number`.

If the table can be successfully imported, it will appear on the table panel.