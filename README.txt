================
KNOWLEDGE MATRIX
================

Content types
=============

Knowledge Profile (Content type)
+++++++++++++++++++++++++++++++

Container of Skills. This content type provides the main funtionality of 
viewing the knowledge, either for all members or for single members.

Fields
------

- ID (Default)
- Title (Default)
- Description (Default)

- Expertises | Groups
  -------------------
  Used for row tagging

- Levels
  ------
  Levels are used to set the competence level on skills

Views
-----

Knowledge: Overview of the competences of all users, available to all users.

Profile: Overview of a user's competences, with ability of changing the skills
when the profile is viewed by the current user.

CV: A CV friendly overview of a user's competences.

Export: CSV export of the Knowledge table



Skill (Content type) (inside Knowledge Profile)
+++++++++++++++++++++++++++++++++++++++++++++++

Fields
------

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

Views
-----

Skill: View on the skill focussed on the current member. Filters the user's
entry in the values field and displays it in the context of all skills. Works
as a click through for setting a new member's skillset.

Change: View to allow changing values through the Profile view on the 
Knowledge Profile when viewed by the current user, with the current user's 
profile active.

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

/ - Edit throught dropdowns in table?
