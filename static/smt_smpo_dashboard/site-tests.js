var passed_msg = "Passed!";
QUnit.test("get_csrf_token_value() test", function(assert) {
    assert.ok(null != get_csrf_token_value(), passed_msg);
});
