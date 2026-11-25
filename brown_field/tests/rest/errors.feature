@acceptance
Feature: A malformed request gets one error format
  A missing or mistyped field, or a direction or an action that does not
  exist, gets 400 "INVALID REQUEST." Every refusal on a game route has the
  body {code, message}.

  Background:
    Given a new player named "ana"

  @api @API-1 @API-2
  Scenario Outline: A malformed request is refused: <case>
    When a client sends <method> <path> with the body <body>
    Then the request is refused with status 400 and the message "INVALID REQUEST."

    Examples:
      | case                     | method | path                                 | body                 |
      | no name                  | POST   | /game/player                         | {}                   |
      | a name that is a number  | POST   | /game/player                         | {"name": 5}          |
      | no body at all           | POST   | /game/player                         | -                    |
      | an unknown direction     | PUT    | /player/{sid}/move/sideways          | -                    |
      | an unknown look          | GET    | /player/{sid}/look/sideways          | -                    |
      | an unknown action        | PUT    | /player/{sid}/item/unknown/use/jump  | -                    |
      | no password, register    | POST   | /accounts                            | {"email": "a@b", "name": "a"} |
      | no password, login       | POST   | /accounts/login                      | {"email": "a@b"}     |
      | no chat text             | POST   | /player/{sid}/chat                   | {}                   |

  @api @API-2 @contested
  Scenario: A URL that is not a route answers with the framework's body
    When a client sends GET /no-such-route with the body -
    Then the response is 404 with the body {"detail": "Not Found"}
