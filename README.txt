================
KNOWLEDGE MATRIX
================

Content types
=============

Knowledge Profile (Content type)
+++++++++++++++++++++++++++++++

- ID (Default)
- Title (Default)
- Description (Default)

- Expertises | Groups
  -------------------
  Used for row tagging

- Levels
  ------
  Levels are used to set the competence level on skills

Skill (Content type) (inside Knowledge Profile)
+++++++++++++++++++++++++++++++++++++++++++++++

- ID (Default) => key, unique
- Title (Default)
- Description (Default) (Searchterms in table)

- Expertise | Group
  -----------------
  Choose one, set on 'Knowledge matrix'

- People / Values
  ---------------
  Per row, values for:
  - userid
  - competence level: empty, X, 1, 2, 3, 4, 5
    +++++++++++++++++++++++++++++++++++++++++
    Empty - The user has answered or answer was prefilled, but has no skill.
    X - Prefilled answer based on the initial csv import.
    1 - opleiding gevolgd/ zelfstudie
    2 - handson
    3 - > 2 jaar ervaring
    4 - > 5 jaar ervaring
    5 - expert
  - show in portlet

Interaction
===========

Anonymous
+++++++++
- Log-in to view or change your knowledge profile (Non-issue, moet altijd inloggen voor sciencelab)

Logged in user
++++++++++++++
- Display user knowledge profile
- 'update knowledge profile' button
  ---------------------------------
  Leads to a one by one walkthrough of all the competences
- 'X value' or 'userid not present' infobox
  -----------------------------------------
  You have not rated any or all of your competence levels, please update your knowledge profile
- Userid not present at all
  -------------------------
  New user, after import, show no table, just 'set knowledge profile' button.

User with reviewer status
+++++++++++++++++++++++++
- Display user knowledge profile
- Buttons for aggregated overviews
  - full table => export to csv?
  - remove non-existent users
  - 
  -
  -

Column order
++++++++++++ 
- Alphabetical within CTeam

TODO
====

V - Legenda's
V - Buttons check!
V - In overview table, give experience a visible que (darker == more experienced)
V - Count value, X == 1
X - Afschermen van volledige tabel
V - translate

V - CSV export
V - Cleanup view

- Edit throught dropdowns in table?
- Portlet


