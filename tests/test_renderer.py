"""Test for jinja rendering capabilities."""
from typing import List, Dict, Optional
import pytest
import pathlib
import logging
from fixtures import ghg_outputs_dict
from heet.io.renderer import JinjaRenderer

test_renderer = JinjaRenderer(
    template_folder=pathlib.Path('./data'))


@pytest.mark.parametrize("required_vars, given_vars, expected_output",
                         [(['a', 'b', 'c'], ['a', 'c'], ['b']),
                          (['a', 'b', 'c'], ['a', 'c', 'b', 'd'], []),
                          (['a', 'b', 'c'], ['b'], ['c', 'a'])])
def test_variable_check(
        required_vars: List, given_vars: List, expected_output: List) -> None:
    missing_vars = test_renderer._find_missing_vars(
        required_vars=required_vars,
        given_vars=given_vars)
    assert set(missing_vars) == set(expected_output)


@pytest.mark.parametrize("check_variables, required_vars, data, txt_output, \
                          log_output",
                         [(False, None, {
                             "greeting_message": "Hello.",
                             "goodbye_message": "Bye Bye."},
                           ['', 'Hello.', '  This is a sample jinja template',
                            'Bye Bye.'],
                           ''),
                          (True, ["greeting_message", "goodbye_message"], {
                              "goodbye_message": "Bye Bye."},
                           ['', '', '  This is a sample jinja template',
                            'Bye Bye.'],
                           'greeting_message')])
def test_message_rendering(
        caplog,
        check_variables: bool,
        required_vars: Optional[List[str]],
        data: Dict,
        txt_output: List[str],
        log_output: str) -> None:
    caplog.set_level(logging.DEBUG)
    test_renderer.check_variables = check_variables
    rendered_output = test_renderer.render(
        template_file='sample_message_template.j2',
        required_vars=required_vars,
        logging=True,
        **data)
    assert rendered_output.as_list_of_strings() == txt_output
    assert log_output in caplog.text


def test_output_rendering(
        ghg_outputs_dict: Dict,
        reservoir_name: str = "Test reservoir") -> None:
    rendered_output = test_renderer.render(
        template_file='ghg_emissions_template_single.j2',
        reservoir_name=reservoir_name, **ghg_outputs_dict)
    output_dict = rendered_output.as_json_dict()
    assert output_dict[reservoir_name] == ghg_outputs_dict
