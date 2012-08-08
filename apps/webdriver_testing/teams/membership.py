# -*- coding: utf-8 -*-

from nose.tools import assert_true, assert_false
from webdriver_base import WebdriverTestCase 

class WebdriverTestCaseWatchPage(WebdriverTestCase):
    def setUp(self):
        WebdriverTestCase.setUp(self)
        #ADD THE TEAMS TEST DATA CREATION HERE

    def test_team__guest(self):
        """Guest (unauthenticated user) sees Sign in message when visiting a team page.

	"""
        team = 'unisubs'
        self.a_team_pg.open_team(team):
        assert_true(getattr(self.a_team_pg, join_team())



    def test_team__apply(self):
	self.a_team_pg.login()
        team = 'application only' #choose a team here that is application only
        self.a_team_pg.open_team(team):
		Then I see a button that reads "Apply to Join"
		When I click the apply button
		Then I see the application modal
		When I click "Submit Application"
		Then I am added to the list of applicantsFeature: Invite a member
	As a team member authorized to invite members
	I want to invite a user to the team
	So that the user can become a member

	# TODO: Should we specify the team as well? To test across multiple
	# teams?
	Scenario: Invite a single user
		Given I am on the team members page
		And I am an admin
		When I click the send invite button
		Then I go to the send invite page
		Given I enter a single valid "<username>"
		And the role selected is "<role>"
		When I click "Send Invites"
		Then the user "<username>" is invited
		When the user "<username>" accepts the invitation
		Then the user "<username>" joins the team with role "<role>"

	# TODO: Set up with real user data
	Examples:
		| username | role |
		| blah | admin |
		| blah | manager |
		| blah | contributor |

	
	Scenario: Invite multiple users
		Given I am on the team members page
		And I am an admin
		When I click the send invite button
		Then I go to the send invite page
		Given I enter a multiple valid "<usernames>"
		And the role selected is "<role>"
		When I click "Send Invites"
		Then the users "<usernames>" are invited
		When any of the users "<usernames>" accept the invitation
		Then the users "<usernames>" join the team with role "<role>"
	
	# TODO: Set up with real user data
	Examples:
		| usernames | role |
		| one, two | admin |
		| one, two, three | manager |
		| one, two, three, four | contributor |Feature: Join a team
    As a user 
    I want to join a team
    So that I can contribute subtitles

    Scenario: An anonymous and must login then is added to the open team.
        Given "normal" user is not a member of any teams
            And I am not logged in as a "normal" user
        When I visit an "open" team
            And I click the signin button
            And I log in as a "normal" user
        Then I see the success message: "You are now a member of this team." 
            And I am a member of the "open" team 
    
    Scenario: A logged in, user joins an open team
        Given "normal" user is not a member of any teams
            And I am logged in as a "normal" user
            And I visit an "open" team
        When I click the join button
            And accept the confirmation alert
        Then I see the success message: "You are now a member of this team." 
            And I am a member of the "open" team

    Scenario: A logged in 'normal' user tries to join an application-only team
        Given "normal" user is not a member of any teams
            And I am logged in as a "normal" user
            And I visit an "application-only" team
        When I click the apply button
        Then the application form is displayed

    Scenario: An anonymous user user tries to join an application-only team
        Given I visit an "application-only" team
        When I click the signin button
            And I log in as a "normal" user
        Then I see the error message: "You cannot join this team." 
Feature: Leave team
	As a member of a team 
	I want to leave the team
    Scenario: Team owner want to leave their team and is the sole admin
        Given I am logged in as the "team-owning" user
        When I leave the team "open" 
        Then I see the error message: "You are the last admin of this team." 

    Scenario Outline: Normal volunteer leaves the team
        Given I am logged in as the "normal" user
            And I have joined the team "<team>"
        When I leave the team "<team>"
        Then I am not a member of the "<team>" team
        Examples:
        | team |
        | open | 

#!/usr/bin/env python
from lettuce import *
from nose.tools import assert_true
from nose.tools import assert_false


@step('"(.*?)" user is not a member of any teams')
def delete_user_from_team_all_teams(self, user):
    world.dj_admin.delete_user_from_all_teams(user)
    

@step('I visit (?:a|an|the) "(.*?)" team')
def open_a_teams_page(self, team_type):
    """Open a/an/the 'open', 'private', 'application-only' or named team page.

    If the string is one of the generic types, then the default team of that type is used.  Alternatively
    a specify team name can be specified by either the stup or full-name (provided no funny characters).
    To be more accurate: use the stub, like "unisubs-test-team" 
    """
    world.a_team_pg.open_a_team_page(team_type)

@step('I (see|click) the (join|apply|signin) button')
def join_button(self, action, button):
    """Verify the presence or click the "Join" button.  
    Both 'click_join()' and 'join_exists()' verify the Button display the correct text based on when the user is 
    logged in or out of the site
    """ 
    if action == "see": assert getattr(world.a_team_pg, button)()
# world.a_team_pg.+button+_exists()
    if action == "click":  getattr(world.a_team_pg, button)()



@step('I (am|am not) a member of the "(.*?)" team')
def is_a_team_member(self, action, team):
    """Check if the currently logged in user is a member of the designated team.

    Valid strings are: a/an/the 'open', 'private', 'application-only' or "named" team page.

    If the string is one of the generic types, then the default team of that type is used.  Alternatively
    a specify team name can be specified by either the stup or full-name (provided no funny characters).
    To be more accurate: use the stub, like "unisubs-test-team"
    """
    if action == "am":
        assert_true(world.a_team_pg.is_member(team))
    else:
        assert_false(world.a_team_pg.is_member(team))
 

@step('I (have|have not) joined the team "(.*?)"')
def join_or_leave_team(self, action, team):
    """Confirm team membership, or perform the action required to get to this state."""

    if action == "have":
        if not world.a_team_pg.is_member(team):
	    world.a_team_pg.open_a_team_page(team)
	    world.a_team_pg.join()
            world.html.handle_js_alert("accept")
    if action == "have not":
        if world.a_team_pg.is_member(team):
            world.my_team_pg.leave_team(team)
            world.html.handle_js_alert("accept")
#    world.a_team_pg.open_a_team_page(team)

@step('I visit a team owned by "(.*?)"')
def open_a_users_team(self, user):
    """Open a team page owned by the specefied user.

    If that user is 'me' then open the team owned by the current looged in user.
    """
    if user == "me":
        world.my_team_pg.open_my_team()
    else:
        try:
            team = [v[0] for k, v in DEFAULT_TEAMS.iteritems() if v[1] == user][0]
        except:
            raise Exception("%user is not a member of the default teams list, \
                            and there isn't a good way to find a team owner in ui yet." % user)

@step('I leave the team "(.*?)"')
def leave_a_team(self, team):
    world.a_team_pg.leave_team(team)

@step('The application form is displayed')
def application_displayed(self):
    world.a_team_pg.application_displayed()
