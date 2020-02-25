# Overview

The Cav Scrapers repo is a collection of tools for the manipulation of data on the 7Cav.us forums and it's Milpacs system.

## Files

### milpacsScraper.py

### milpacEditor.py

This file is used to:

* Add award entries
* Add service record entries
* Upload uniform files

Currently, if the file is executed directly it will give you instructions for doing a bulk processing of any of the options listed above. To perform a bulk processing you need to have a .csv file with the correct items in each row. The requirements for each type of bulk processing are listed below.

The format for the row listing is: `<index number>` (`<variable type>`): `<description>`

#### Bulk Service Records

Each row must contain the following:
> 0 (int): Trooper's Milpac ID.
>
> 1 (int): Trooper's roster ID.
>
> 2 (str): Service record entry text.
>
> 3 (str): Service record entry date. Must be following Format: yyyy-mm-dd (Ex: "2020-01-19")
>
> 4 (str) [OPTIONAL]: Path to citation file. Not the folder, the actual file.``

#### Bulk Awards

Each row must contain the following:
> 0 (int): Trooper's Milpac ID.
>
> 1 (int): Trooper's roster ID.
>
> 2 (str): Award name, as it appears in Milpacs. Case sensitive.
>
> 3 (str): Service record entry date. Must be following Format: yyyy-mm-dd (Ex: "2020-01-19").
>
> 4 (str): Path to citation file. Not the folder, the actual file. If not using a citation, put an empty string.
>
> 5 (str) [OPTIONAL]: Award details.

#### Bulk Uniform Upload

Each row must contain the following
> 0 (int): Trooper's Milpac ID.
>
> 1 (int): Trooper's roster ID.
>
> 2 (str): Path to uniform file. The file, not the folder.