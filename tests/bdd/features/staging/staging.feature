Feature: Testbed for Tests
    in order to do a small test
    as a test developer
    I need to test one scenario at a time

    Scenario: Create and approve a Testcase with steps
        Given I create a new user with name "Joe Approver"
        and I activate the user with that name
        And I create a new role with name "Approvationalist" with the following permissions:
            | permissionCode               |
            | PERMISSION_TEST_CASE_APPROVE |
        Then the role with that name has the following permissions:
            | permissionCode               |
            | PERMISSION_TEST_CASE_APPROVE |
        And I add the role with that name to the user with name "Joe Approver"
        Then the user with that name has the role with that name
        And a testcase with name "Come on fhqwhgads" does not exist
        when I create a new testcase with that name
        then a testcase with that name exists
        and when I add these steps to the testcase with that name:
            | name      | stepNumber | estimatedTimeInMin | instruction    | expectedResult        |
            | Mockery   | 1          | 5                  | Go this way    | They went this way    |
            | Flockery  | 2          | 2                  | Go that way    | They went that way    |
            | Chockery  | 3          | 4                  | Go my way      | They went my way      |
            | Trockery  | 4          | 1                  | Go the highway | They went the highway |
            | Blockery  | 5          | 25                 | Just go away   | They went away        |
        then the testcase with that name has these steps:
            | name      | stepNumber | estimatedTimeInMin | instruction    | expectedResult        |
            | Mockery   | 1          | 5                  | Go this way    | They went this way    |
            | Flockery  | 2          | 2                  | Go that way    | They went that way    |
            | Chockery  | 3          | 4                  | Go my way      | They went my way      |
            | Trockery  | 4          | 1                  | Go the highway | They went the highway |
            | Blockery  | 5          | 25                 | Just go away   | They went away        |
        and when the user with name "Joe Approver" approves the testcase with that name
        then the testcase with that name has status of approved

            