## APCD Portal

https://txapcd.org/

## Documentation

> [!TIP]
> This project is built as a customization of a TACC <abbr title="Content Management System">CMS</abbr> website. To manage this project's CMS, reference [Core-CMS-Template Docs][core-cms-template-docs]. To develop this project's custom code, keep reading.

## Quick Start

1. Navigate to project directory:\
    <sup>This is a CMS that contains a Portal client application.</sup>
    ```sh
    cd to acpd_cms
    ```
2. Configure the project:
    - Create a `/cms/src/taccsite_cms/secrets.py` with content from ["Stache" secret `APCD DEV CMS`](https://stache.utexas.edu/entry/c6a600467c02fcf0c902c229bd145118).
    - NOTE: APCD_DATABASE.database should be 'pipeline2' for local development
3. Start the CMS website:\
    <sup>This command will also first build the CMS as needed.</sup>
    ```sh
    make start
    ```
4. Navigate to client app:
    ```sh
    cd apcd_cms/src/client
    ```
5. Install dependencies:
    ```sh
    npm ci
    ```
6. Start the client app:
    ```sh
    npm run dev
    ```
7. Change code and observe updates live in the browser.


## Convert Existing Django App Page to React App Page

### Backend

1. Update `urls.py`:
   - Make the default page return as\
       `TemplateView.as_view(template_name='<template_name')`
   - Add API endpoints.\
       _These endpoints are used in [Client](#client)._

2. Update `views.py`:
   - `import` `JsonResponse`
   - Remove Template building.
   - Adjust context to return `json`.
   - Send `JsonResponse`.


### Client

1. Define hook:
    - Add method to retrieve data from server.
	- Add & Export `type`s in `index.ts`.

2. Defining component:
    - Add one or more components as a `.tsx` file.
    - Export the component.
	- Add `export`s in `index.ts`.

3. Update `apcd_cms/src/client/src/main.tsx`:
    - `import` the component.
    - Map (via `componentMap`) a unique ID to the component.
	

### Template

- Update first line:
    - from `{% extends "standard.html" %}`
    - to `{% extends "apcd_cms/templates/standard.html" %}`
- Add an element where the component will render e.g.
   ```html
   <div id="list-registrations-root"></div>
   ```

   _Give the element its unique `id` as defined in `main.tsx`._




<!-- Link Aliases -->

[Core CMS]: https://github.com/TACC/Core-CMS
[Core CMS Template]: https://github.com/TACC/Core-CMS-Template
[Core Portal Deployments]: https://github.com/TACC/Core-Portal-Deployments

[core-cms-template-docs]: https://github.com/TACC/Core-CMS-Template/blob/v0.1.3/docs/README.md#tacc-custom-cms
