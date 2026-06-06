% ── Project Metadata ─────────────────────────────────────
project_metadata('env2llm', '0.1.5', 'python').

% ── Project Files ────────────────────────────────────────
project_file('app.doql.less', 231, 'less').
project_file('project.sh', 59, 'shell').
project_file('src/env2llm/__init__.py', 44, 'python').
project_file('src/env2llm/__main__.py', 4, 'python').
project_file('src/env2llm/_runtime_health.py', 32, 'python').
project_file('src/env2llm/adapters/__init__.py', 7, 'python').
project_file('src/env2llm/adapters/mcp.py', 143, 'python').
project_file('src/env2llm/adapters/rest.py', 107, 'python').
project_file('src/env2llm/artifact_layout.py', 2, 'python').
project_file('src/env2llm/bootstrap.py', 106, 'python').
project_file('src/env2llm/bridge.py', 226, 'python').
project_file('src/env2llm/cli.py', 64, 'python').
project_file('src/env2llm/doql/__init__.py', 49, 'python').
project_file('src/env2llm/doql/context_blocks.py', 235, 'python').
project_file('src/env2llm/doql/models.py', 135, 'python').
project_file('src/env2llm/doql/parse.py', 483, 'python').
project_file('src/env2llm/doql/render.py', 50, 'python').
project_file('src/env2llm/doql/runtime.py', 207, 'python').
project_file('src/env2llm/doql_context.py', 27, 'python').
project_file('src/env2llm/env.py', 73, 'python').
project_file('src/env2llm/formats/__init__.py', 60, 'python').
project_file('src/env2llm/formats/doql_less.py', 12, 'python').
project_file('src/env2llm/formats/json_fmt.py', 14, 'python').
project_file('src/env2llm/formats/markdown.py', 53, 'python').
project_file('src/env2llm/formats/yaml_fmt.py', 14, 'python').
project_file('src/env2llm/generate.py', 209, 'python').
project_file('src/env2llm/integrators/__init__.py', 2, 'python').
project_file('src/env2llm/integrators/_service_factory.py', 50, 'python').
project_file('src/env2llm/integrators/mcp_server.py', 137, 'python').
project_file('src/env2llm/integrators/mqtt_bridge.py', 146, 'python').
project_file('src/env2llm/integrators/rest_server.py', 115, 'python').
project_file('src/env2llm/ir.py', 316, 'python').
project_file('src/env2llm/layout.py', 267, 'python').
project_file('src/env2llm/policy/__init__.py', 5, 'python').
project_file('src/env2llm/policy/desktop.py', 176, 'python').
project_file('src/env2llm/policy/invoice.py', 53, 'python').
project_file('src/env2llm/policy/process.py', 338, 'python').
project_file('src/env2llm/policy/validations.py', 74, 'python').
project_file('src/env2llm/probes/__init__.py', 6, 'python').
project_file('src/env2llm/probes/desktop.py', 143, 'python').
project_file('src/env2llm/registry.py', 231, 'python').
project_file('src/env2llm/render/__init__.py', 4, 'python').
project_file('src/env2llm/render/doql/__init__.py', 6, 'python').
project_file('src/env2llm/render/doql/blocks.py', 341, 'python').
project_file('src/env2llm/render/doql/helpers.py', 46, 'python').
project_file('src/env2llm/render/doql/render.py', 51, 'python').
project_file('src/env2llm/runtimes.py', 178, 'python').
project_file('src/env2llm/service/__init__.py', 6, 'python').
project_file('src/env2llm/service/registry_service.py', 166, 'python').
project_file('src/env2llm/sources.py', 68, 'python').
project_file('src/env2llm/system_map_bridge.py', 2, 'python').
project_file('src/env2llm/system_map_generator.py', 2, 'python').
project_file('src/env2llm/system_map_ir.py', 2, 'python').
project_file('src/env2llm/system_map_models.py', 49, 'python').
project_file('src/env2llm/system_map_render.py', 2, 'python').
project_file('src/env2llm/system_map_runtimes.py', 2, 'python').
project_file('src/env2llm/transport/__init__.py', 6, 'python').
project_file('src/env2llm/transport/mqtt.py', 153, 'python').
project_file('tests/conftest.py', 24, 'python').
project_file('tests/test_desktop_probe.py', 69, 'python').
project_file('tests/test_doql_context.py', 312, 'python').
project_file('tests/test_formats.py', 24, 'python').
project_file('tests/test_integrators.py', 91, 'python').
project_file('tests/test_mqtt.py', 73, 'python').
project_file('tests/test_registry_service.py', 92, 'python').
project_file('tests/test_system_map_ir.py', 140, 'python').
project_file('tree.sh', 2, 'shell').

% ── Python Functions ─────────────────────────────────────
python_function('src/env2llm/_runtime_health.py', 'runtime_id_for_intent', 1, 6, 1).
python_function('src/env2llm/adapters/mcp.py', '_mcp_error', 1, 1, 0).
python_function('src/env2llm/bootstrap.py', 'project_artifact_root', 1, 1, 2).
python_function('src/env2llm/bootstrap.py', 'ensure_environment_map', 1, 9, 22).
python_function('src/env2llm/bootstrap.py', 'ensure_doql_registry', 1, 1, 1).
python_function('src/env2llm/bridge.py', '_mime_for_artifact', 1, 4, 3).
python_function('src/env2llm/bridge.py', '_process_from_ctx', 1, 12, 10).
python_function('src/env2llm/bridge.py', 'task_context_to_system_map', 1, 25, 20).
python_function('src/env2llm/bridge.py', '_command_to_ir', 1, 12, 8).
python_function('src/env2llm/bridge.py', 'doql_file_to_system_map', 1, 1, 3).
python_function('src/env2llm/cli.py', 'build_parser', 0, 1, 4).
python_function('src/env2llm/cli.py', 'main', 1, 1, 6).
python_function('src/env2llm/doql/context_blocks.py', 'render_context_header', 1, 1, 0).
python_function('src/env2llm/doql/context_blocks.py', 'render_context_environment', 1, 3, 5).
python_function('src/env2llm/doql/context_blocks.py', 'render_context_data', 1, 2, 4).
python_function('src/env2llm/doql/context_blocks.py', 'render_context_artifacts', 1, 4, 6).
python_function('src/env2llm/doql/context_blocks.py', 'render_context_commands', 1, 6, 5).
python_function('src/env2llm/doql/context_blocks.py', 'render_context_resources', 1, 5, 5).
python_function('src/env2llm/doql/context_blocks.py', 'render_context_access', 1, 4, 4).
python_function('src/env2llm/doql/context_blocks.py', 'render_context_runtimes', 1, 10, 4).
python_function('src/env2llm/doql/context_blocks.py', 'render_context_capabilities', 1, 2, 1).
python_function('src/env2llm/doql/context_blocks.py', 'render_context_workflow_history', 1, 6, 5).
python_function('src/env2llm/doql/context_blocks.py', 'render_context_process', 1, 18, 1).
python_function('src/env2llm/doql/context_blocks.py', 'render_context_process_access', 1, 7, 2).
python_function('src/env2llm/doql/context_blocks.py', 'render_context_paths', 1, 5, 2).
python_function('src/env2llm/doql/context_blocks.py', 'render_context_conversation', 1, 3, 1).
python_function('src/env2llm/doql/parse.py', '_parse_value', 1, 10, 8).
python_function('src/env2llm/doql/parse.py', '_parse_block_body', 1, 2, 3).
python_function('src/env2llm/doql/parse.py', '_split_csv', 1, 3, 3).
python_function('src/env2llm/doql/parse.py', '_parse_command_body', 1, 1, 5).
python_function('src/env2llm/doql/parse.py', '_parse_resource_body', 1, 1, 5).
python_function('src/env2llm/doql/parse.py', '_parse_access_body', 1, 1, 5).
python_function('src/env2llm/doql/parse.py', '_parse_runtime_body', 1, 1, 5).
python_function('src/env2llm/doql/parse.py', '_parse_validation_body', 1, 1, 4).
python_function('src/env2llm/doql/parse.py', '_parse_artifact_body', 1, 3, 4).
python_function('src/env2llm/doql/parse.py', '_apply_context_metadata', 2, 3, 2).
python_function('src/env2llm/doql/parse.py', '_apply_conversation_block', 2, 1, 2).
python_function('src/env2llm/doql/parse.py', '_apply_capabilities_block', 2, 5, 4).
python_function('src/env2llm/doql/parse.py', '_apply_process_block', 2, 9, 6).
python_function('src/env2llm/doql/parse.py', '_apply_process_access_block', 2, 4, 2).
python_function('src/env2llm/doql/parse.py', '_apply_paths_block', 2, 3, 2).
python_function('src/env2llm/doql/parse.py', '_apply_context_block', 3, 10, 9).
python_function('src/env2llm/doql/parse.py', '_append_collection_blocks', 2, 12, 8).
python_function('src/env2llm/doql/parse.py', 'load_doql_context', 1, 2, 8).
python_function('src/env2llm/doql/parse.py', '_repo_root_from_example', 1, 2, 0).
python_function('src/env2llm/doql/parse.py', '_command_transport', 1, 3, 1).
python_function('src/env2llm/doql/parse.py', 'load_platform_map', 1, 18, 10).
python_function('src/env2llm/doql/parse.py', 'load_commands_from_services_yaml', 1, 14, 10).
python_function('src/env2llm/doql/parse.py', 'enrich_task_context_from_client', 2, 19, 10).
python_function('src/env2llm/doql/parse.py', 'parse_fixture_metadata', 1, 10, 11).
python_function('src/env2llm/doql/parse.py', 'collect_task_context', 1, 19, 26).
python_function('src/env2llm/doql/render.py', 'render_doql_context', 1, 1, 16).
python_function('src/env2llm/doql/render.py', 'write_doql_context', 2, 1, 4).
python_function('src/env2llm/doql/runtime.py', 'resolve_doql_context_path', 0, 1, 1).
python_function('src/env2llm/doql/runtime.py', 'context_inline_payload', 1, 14, 10).
python_function('src/env2llm/doql/runtime.py', 'load_doql_inline_from_env', 0, 2, 3).
python_function('src/env2llm/doql/runtime.py', 'merge_inline_context', 2, 8, 8).
python_function('src/env2llm/doql/runtime.py', 'autofill_entities', 3, 8, 6).
python_function('src/env2llm/doql/runtime.py', '_inline_data_key', 1, 1, 1).
python_function('src/env2llm/doql/runtime.py', '_apply_conversation_flag', 3, 6, 1).
python_function('src/env2llm/doql/runtime.py', '_add_short_inline_alias', 4, 5, 3).
python_function('src/env2llm/doql/runtime.py', '_split_missing_ref', 2, 4, 4).
python_function('src/env2llm/doql/runtime.py', '_canonical_field', 1, 1, 2).
python_function('src/env2llm/doql/runtime.py', '_autofill_value', 3, 2, 3).
python_function('src/env2llm/doql/runtime.py', '_candidate_data_keys', 2, 1, 0).
python_function('src/env2llm/doql/runtime.py', '_value_from_data', 2, 4, 0).
python_function('src/env2llm/doql/runtime.py', '_value_from_artifacts', 2, 6, 0).
python_function('src/env2llm/doql/runtime.py', '_needs_field', 2, 1, 1).
python_function('src/env2llm/env.py', 'mask_secret', 1, 3, 1).
python_function('src/env2llm/env.py', 'collect_environment', 0, 13, 10).
python_function('src/env2llm/env.py', 'merge_environment', 2, 3, 2).
python_function('src/env2llm/formats/__init__.py', 'normalize_format', 1, 2, 4).
python_function('src/env2llm/formats/__init__.py', 'render_format', 2, 2, 6).
python_function('src/env2llm/formats/__init__.py', 'default_output_name', 1, 2, 1).
python_function('src/env2llm/formats/doql_less.py', 'render_doql_less', 2, 1, 1).
python_function('src/env2llm/formats/json_fmt.py', 'render_json', 2, 1, 2).
python_function('src/env2llm/formats/markdown.py', 'render_markdown', 2, 22, 7).
python_function('src/env2llm/formats/yaml_fmt.py', 'render_yaml', 2, 1, 2).
python_function('src/env2llm/generate.py', 'build_introspection_payload', 1, 12, 19).
python_function('src/env2llm/generate.py', '_bootstrap_system_map', 1, 2, 3).
python_function('src/env2llm/generate.py', '_litellm_complete', 2, 3, 5).
python_function('src/env2llm/generate.py', '_parse_llm_json', 1, 5, 7).
python_function('src/env2llm/generate.py', 'generate_system_map', 1, 8, 14).
python_function('src/env2llm/integrators/_service_factory.py', 'build_registry_service', 1, 4, 6).
python_function('src/env2llm/integrators/_service_factory.py', 'attach_mqtt_refresh_listener', 1, 2, 5).
python_function('src/env2llm/integrators/mcp_server.py', '_jsonrpc_response', 2, 1, 0).
python_function('src/env2llm/integrators/mcp_server.py', '_jsonrpc_error', 4, 2, 0).
python_function('src/env2llm/integrators/mcp_server.py', '_write_json', 1, 1, 3).
python_function('src/env2llm/integrators/mcp_server.py', '_log', 1, 1, 1).
python_function('src/env2llm/integrators/mcp_server.py', 'handle_message', 1, 9, 6).
python_function('src/env2llm/integrators/mcp_server.py', 'run_stdio', 0, 6, 10).
python_function('src/env2llm/integrators/mcp_server.py', 'main', 1, 3, 5).
python_function('src/env2llm/integrators/mqtt_bridge.py', 'run_bridge', 0, 5, 10).
python_function('src/env2llm/integrators/mqtt_bridge.py', 'publish_once', 0, 4, 8).
python_function('src/env2llm/integrators/mqtt_bridge.py', 'main', 1, 4, 10).
python_function('src/env2llm/integrators/rest_server.py', 'run_server', 0, 3, 9).
python_function('src/env2llm/integrators/rest_server.py', 'main', 1, 3, 5).
python_function('src/env2llm/layout.py', 'artifact_root', 1, 1, 2).
python_function('src/env2llm/layout.py', '_chmod_writable', 1, 2, 1).
python_function('src/env2llm/layout.py', '_force_remove_path', 1, 7, 10).
python_function('src/env2llm/layout.py', 'clean_artifact_root', 1, 9, 7).
python_function('src/env2llm/layout.py', 'clean_all_example_artifacts', 1, 5, 6).
python_function('src/env2llm/layout.py', 'example_fixtures_dir', 1, 1, 2).
python_function('src/env2llm/layout.py', 'ensure_layout', 1, 1, 3).
python_function('src/env2llm/layout.py', 'resolve_registry_path', 0, 9, 5).
python_function('src/env2llm/layout.py', 'write_registry', 2, 2, 4).
python_function('src/env2llm/layout.py', 'current_run_id', 1, 2, 4).
python_function('src/env2llm/layout.py', 'run_dir', 2, 2, 4).
python_function('src/env2llm/layout.py', 'write_turn_snapshot', 1, 4, 13).
python_function('src/env2llm/layout.py', 'write_reflection_snapshot', 1, 1, 7).
python_function('src/env2llm/layout.py', 'write_last_run_report', 2, 1, 6).
python_function('src/env2llm/policy/desktop.py', 'desktop_probe_enabled', 0, 2, 3).
python_function('src/env2llm/policy/desktop.py', '_ensure_desktop_runtime', 1, 2, 3).
python_function('src/env2llm/policy/desktop.py', '_ensure_desktop_resource', 1, 3, 3).
python_function('src/env2llm/policy/desktop.py', '_ensure_desktop_commands', 1, 6, 6).
python_function('src/env2llm/policy/desktop.py', '_ensure_desktop_access', 1, 5, 3).
python_function('src/env2llm/policy/desktop.py', '_mirror_desktop_summary', 1, 12, 3).
python_function('src/env2llm/policy/desktop.py', 'apply_desktop_probe', 1, 6, 11).
python_function('src/env2llm/policy/invoice.py', 'is_invoice_example', 1, 2, 1).
python_function('src/env2llm/policy/invoice.py', 'apply_invoice_policies', 1, 5, 5).
python_function('src/env2llm/policy/invoice.py', 'apply_invoice_context', 1, 3, 6).
python_function('src/env2llm/policy/process.py', '_as_list', 1, 8, 4).
python_function('src/env2llm/policy/process.py', '_deep_merge_process', 2, 5, 5).
python_function('src/env2llm/policy/process.py', '_load_nlp2dsl_payload', 1, 12, 7).
python_function('src/env2llm/policy/process.py', 'load_platform_process_defaults', 1, 4, 6).
python_function('src/env2llm/policy/process.py', '_merge_access', 1, 5, 4).
python_function('src/env2llm/policy/process.py', '_merge_paths', 1, 4, 3).
python_function('src/env2llm/policy/process.py', 'process_policy_from_profile_block', 1, 5, 14).
python_function('src/env2llm/policy/process.py', '_mapping_block', 2, 2, 2).
python_function('src/env2llm/policy/process.py', '_apply_nlp_policy', 2, 5, 4).
python_function('src/env2llm/policy/process.py', '_apply_autonomous_policy', 2, 5, 4).
python_function('src/env2llm/policy/process.py', '_apply_llm_policy', 2, 4, 3).
python_function('src/env2llm/policy/process.py', '_intract_flags', 1, 2, 2).
python_function('src/env2llm/policy/process.py', '_normalized_mode', 1, 2, 0).
python_function('src/env2llm/policy/process.py', '_process_policy_from_parts', 0, 1, 5).
python_function('src/env2llm/policy/process.py', '_merge_conversation_from_profile', 2, 5, 4).
python_function('src/env2llm/policy/process.py', 'merge_process_config', 0, 4, 5).
python_function('src/env2llm/policy/process.py', 'apply_process_policies', 1, 8, 10).
python_function('src/env2llm/policy/process.py', 'effective_nlp_parser_mode', 1, 5, 1).
python_function('src/env2llm/policy/process.py', 'process_policy_to_doql_dict', 1, 2, 0).
python_function('src/env2llm/policy/process.py', 'process_scope_denied', 1, 12, 6).
python_function('src/env2llm/policy/validations.py', '_parse_profile_validation_by_code', 1, 4, 3).
python_function('src/env2llm/policy/validations.py', '_parse_profile_validation_by_type', 1, 5, 4).
python_function('src/env2llm/policy/validations.py', '_parse_profile_validation_shorthand', 1, 10, 6).
python_function('src/env2llm/policy/validations.py', 'parse_profile_validation', 1, 5, 4).
python_function('src/env2llm/policy/validations.py', 'parse_profile_validations', 1, 4, 2).
python_function('src/env2llm/policy/validations.py', 'apply_profile_validations', 2, 3, 2).
python_function('src/env2llm/probes/desktop.py', '_run_text', 1, 4, 2).
python_function('src/env2llm/probes/desktop.py', '_is_browser_title', 1, 1, 2).
python_function('src/env2llm/probes/desktop.py', 'parse_wmctrl_listing', 1, 3, 8).
python_function('src/env2llm/probes/desktop.py', '_probe_display_geometry', 0, 5, 6).
python_function('src/env2llm/probes/desktop.py', '_probe_active_window_id', 0, 4, 5).
python_function('src/env2llm/probes/desktop.py', 'collect_desktop_probe', 0, 15, 13).
python_function('src/env2llm/registry.py', 'entities_to_data', 2, 5, 4).
python_function('src/env2llm/registry.py', 'merge_execution_observation', 3, 2, 5).
python_function('src/env2llm/registry.py', '_merge_execution_header', 2, 1, 4).
python_function('src/env2llm/registry.py', '_execution_steps', 1, 4, 2).
python_function('src/env2llm/registry.py', '_merge_execution_step', 3, 4, 6).
python_function('src/env2llm/registry.py', '_step_output', 1, 4, 2).
python_function('src/env2llm/registry.py', '_merge_send_invoice_output', 3, 3, 2).
python_function('src/env2llm/registry.py', '_merge_generate_invoice_output', 2, 3, 1).
python_function('src/env2llm/registry.py', '_merge_workflow_id', 2, 3, 2).
python_function('src/env2llm/registry.py', 'merge_registry_observations', 2, 11, 9).
python_function('src/env2llm/registry.py', 'refresh_doql_registry', 1, 10, 16).
python_function('src/env2llm/registry.py', 'refresh_doql_registry_from_state', 1, 1, 1).
python_function('src/env2llm/render/doql/blocks.py', 'render_header', 1, 1, 2).
python_function('src/env2llm/render/doql/blocks.py', 'render_environment_block', 1, 2, 5).
python_function('src/env2llm/render/doql/blocks.py', 'render_data_block', 1, 3, 4).
python_function('src/env2llm/render/doql/blocks.py', 'render_artifacts_block', 1, 6, 6).
python_function('src/env2llm/render/doql/blocks.py', 'render_desktop_block', 1, 8, 7).
python_function('src/env2llm/render/doql/blocks.py', 'render_runtimes_block', 1, 8, 4).
python_function('src/env2llm/render/doql/blocks.py', 'render_commands_block', 1, 9, 5).
python_function('src/env2llm/render/doql/blocks.py', 'render_resources_block', 1, 5, 5).
python_function('src/env2llm/render/doql/blocks.py', 'render_access_block', 1, 4, 4).
python_function('src/env2llm/render/doql/blocks.py', 'render_capabilities_block', 1, 2, 1).
python_function('src/env2llm/render/doql/blocks.py', 'render_workflow_history_block', 1, 3, 4).
python_function('src/env2llm/render/doql/blocks.py', 'render_conversation_block', 1, 3, 3).
python_function('src/env2llm/render/doql/blocks.py', 'render_process_block', 1, 3, 3).
python_function('src/env2llm/render/doql/blocks.py', 'render_process_access_block', 1, 7, 3).
python_function('src/env2llm/render/doql/blocks.py', 'render_paths_block', 1, 5, 3).
python_function('src/env2llm/render/doql/blocks.py', 'render_schedules_block', 1, 3, 5).
python_function('src/env2llm/render/doql/blocks.py', 'render_deploy_block', 1, 3, 3).
python_function('src/env2llm/render/doql/blocks.py', 'render_generated_services_block', 1, 6, 5).
python_function('src/env2llm/render/doql/blocks.py', 'render_validations_block', 1, 5, 4).
python_function('src/env2llm/render/doql/helpers.py', 'esc_str', 1, 1, 1).
python_function('src/env2llm/render/doql/helpers.py', 'esc_str_full', 1, 1, 1).
python_function('src/env2llm/render/doql/helpers.py', 'bool_lit', 1, 2, 0).
python_function('src/env2llm/render/doql/helpers.py', 'join_csv', 1, 1, 1).
python_function('src/env2llm/render/doql/helpers.py', 'data_value_line', 2, 3, 3).
python_function('src/env2llm/render/doql/helpers.py', 'history_value_line', 2, 4, 3).
python_function('src/env2llm/render/doql/helpers.py', 'process_field_line', 2, 3, 2).
python_function('src/env2llm/render/doql/render.py', 'render_system_map_doql', 1, 1, 21).
python_function('src/env2llm/runtimes.py', '_repo_root_from_example', 1, 2, 0).
python_function('src/env2llm/runtimes.py', 'load_example_profile', 2, 7, 6).
python_function('src/env2llm/runtimes.py', 'resolve_command_runtime', 1, 8, 2).
python_function('src/env2llm/runtimes.py', 'build_runtimes_for_example', 1, 18, 12).
python_function('src/env2llm/system_map_models.py', '_annotation_for_field', 1, 11, 2).
python_function('src/env2llm/system_map_models.py', 'command_input_model', 1, 4, 5).
python_function('src/env2llm/system_map_models.py', 'build_command_registry', 1, 2, 1).
python_function('src/env2llm/system_map_models.py', 'validate_config_against_map', 3, 2, 5).
python_function('src/env2llm/transport/mqtt.py', 'mqtt_available', 0, 1, 0).
python_function('src/env2llm/transport/mqtt.py', 'mqtt_missing_message', 0, 2, 0).
python_function('src/env2llm/transport/mqtt.py', 'mqtt_enabled', 0, 2, 3).
python_function('tests/conftest.py', 'nlp2dsl_root', 0, 1, 1).
python_function('tests/conftest.py', 'invoice_example_dir', 0, 2, 3).
python_function('tests/test_desktop_probe.py', 'test_parse_wmctrl_listing_detects_geometry_and_browser', 0, 8, 2).
python_function('tests/test_desktop_probe.py', 'test_apply_desktop_probe_adds_runtime_commands_and_doql_block', 1, 11, 8).
python_function('tests/test_doql_context.py', 'test_load_doql_context_all_supported_blocks', 1, 34, 3).
python_function('tests/test_doql_context.py', 'test_doql_roundtrip_preserves_core_fields', 1, 7, 5).
python_function('tests/test_doql_context.py', 'test_autofill_entities_from_data_and_aliases', 0, 4, 2).
python_function('tests/test_doql_context.py', 'test_autofill_entities_from_artifact_values', 0, 3, 3).
python_function('tests/test_doql_context.py', 'test_autofill_entities_skips_optional_attachment_path', 0, 3, 3).
python_function('tests/test_doql_context.py', 'test_merge_inline_context_promotes_short_aliases', 0, 5, 2).
python_function('tests/test_doql_context.py', 'test_autofill_entities_disabled_returns_original_object', 0, 3, 2).
python_function('tests/test_doql_context.py', 'test_load_doql_context_parses_validations', 1, 6, 4).
python_function('tests/test_doql_context.py', 'test_validations_doql_roundtrip_via_system_map', 1, 4, 6).
python_function('tests/test_formats.py', 'test_render_json_yaml_markdown', 0, 5, 4).
python_function('tests/test_integrators.py', '_fake_service', 1, 1, 5).
python_function('tests/test_integrators.py', 'test_rest_adapter_routes', 1, 7, 3).
python_function('tests/test_integrators.py', 'test_mcp_adapter_tools', 1, 4, 3).
python_function('tests/test_integrators.py', 'test_rest_server_health', 1, 4, 20).
python_function('tests/test_mqtt.py', '_install_fake_paho', 1, 1, 4).
python_function('tests/test_mqtt.py', 'test_mqtt_publish_topics', 1, 8, 9).
python_function('tests/test_registry_service.py', 'test_registry_service_render_and_desktop', 2, 7, 13).
python_function('tests/test_registry_service.py', 'test_registry_service_refresh_publishes_mqtt', 2, 3, 8).
python_function('tests/test_system_map_ir.py', 'test_system_map_validate_step_config', 0, 3, 5).
python_function('tests/test_system_map_ir.py', 'test_dynamic_command_input_model', 0, 3, 7).
python_function('tests/test_system_map_ir.py', 'test_task_context_to_system_map_and_render', 1, 12, 7).
python_function('tests/test_system_map_ir.py', 'test_build_runtimes_for_01_invoice', 1, 9, 2).
python_function('tests/test_system_map_ir.py', 'test_resolve_command_runtime', 0, 4, 1).
python_function('tests/test_system_map_ir.py', 'test_doql_roundtrip_runtimes', 1, 3, 7).
python_function('tests/test_system_map_ir.py', 'test_generate_system_map_01_invoice', 1, 3, 2).

% ── Python Classes ───────────────────────────────────────
python_class('src/env2llm/adapters/mcp.py', 'McpAdapter').
python_method('McpAdapter', '__init__', 1, 1, 0).
python_method('McpAdapter', 'call_tool', 2, 13, 15).
python_class('src/env2llm/adapters/rest.py', 'RestAdapter').
python_method('RestAdapter', '__init__', 1, 1, 0).
python_method('RestAdapter', 'match_route', 3, 5, 2).
python_method('RestAdapter', 'dispatch', 1, 13, 18).
python_method('RestAdapter', 'handle_http', 2, 4, 5).
python_class('src/env2llm/doql/models.py', 'DoqlArtifact').
python_class('src/env2llm/doql/models.py', 'DoqlRuntime').
python_class('src/env2llm/doql/models.py', 'DoqlCommand').
python_class('src/env2llm/doql/models.py', 'DoqlResource').
python_class('src/env2llm/doql/models.py', 'DoqlAccess').
python_class('src/env2llm/doql/models.py', 'DoqlProcessPolicy').
python_class('src/env2llm/doql/models.py', 'DoqlTaskContext').
python_method('DoqlTaskContext', 'entity_values', 1, 5, 3).
python_method('DoqlTaskContext', 'command', 1, 3, 0).
python_method('DoqlTaskContext', 'required_fields_for', 1, 3, 2).
python_method('DoqlTaskContext', 'runtime_for', 1, 6, 3).
python_class('src/env2llm/integrators/rest_server.py', 'Env2LLMRequestHandler').
python_method('Env2LLMRequestHandler', 'log_message', 1, 1, 0).
python_method('Env2LLMRequestHandler', '_read_body', 0, 3, 3).
python_method('Env2LLMRequestHandler', '_send', 2, 1, 8).
python_method('Env2LLMRequestHandler', '_handle', 1, 2, 3).
python_method('Env2LLMRequestHandler', 'do_GET', 0, 1, 1).
python_method('Env2LLMRequestHandler', 'do_POST', 0, 1, 1).
python_class('src/env2llm/ir.py', 'MimeTypeSpec').
python_class('src/env2llm/ir.py', 'RuntimeSpecIR').
python_class('src/env2llm/ir.py', 'ProtocolSpec').
python_class('src/env2llm/ir.py', 'FieldSpec').
python_class('src/env2llm/ir.py', 'CommandSchemaIR').
python_method('CommandSchemaIR', 'required_names', 0, 3, 0).
python_method('CommandSchemaIR', 'optional_names', 0, 3, 0).
python_class('src/env2llm/ir.py', 'ResourceSpecIR').
python_class('src/env2llm/ir.py', 'AccessGrantIR').
python_class('src/env2llm/ir.py', 'ArtifactSpecIR').
python_class('src/env2llm/ir.py', 'ConversationPolicyIR').
python_class('src/env2llm/ir.py', 'ProcessAccessScopeIR').
python_class('src/env2llm/ir.py', 'ProcessPathsIR').
python_class('src/env2llm/ir.py', 'ProcessPolicyIR').
python_class('src/env2llm/ir.py', 'ScheduleSpecIR').
python_class('src/env2llm/ir.py', 'GeneratedServiceIR').
python_class('src/env2llm/ir.py', 'DeploySpecIR').
python_class('src/env2llm/ir.py', 'ProfileValidationIR').
python_class('src/env2llm/ir.py', 'DesktopWindowIR').
python_class('src/env2llm/ir.py', 'DesktopDisplayIR').
python_class('src/env2llm/ir.py', 'DesktopProbeIR').
python_class('src/env2llm/ir.py', 'SystemMapIR').
python_method('SystemMapIR', 'command', 1, 3, 0).
python_method('SystemMapIR', 'runtime', 1, 3, 0).
python_method('SystemMapIR', 'runtime_for_command', 1, 3, 2).
python_method('SystemMapIR', 'validate_step_config', 2, 7, 5).
python_class('src/env2llm/service/registry_service.py', 'RegistryService').
python_method('RegistryService', '__post_init__', 0, 2, 2).
python_method('RegistryService', 'registry_path', 0, 3, 2).
python_method('RegistryService', 'load', 0, 2, 3).
python_method('RegistryService', 'refresh', 0, 4, 4).
python_method('RegistryService', 'get_ir', 0, 3, 2).
python_method('RegistryService', 'render', 1, 1, 2).
python_method('RegistryService', 'to_dict', 0, 1, 2).
python_method('RegistryService', 'desktop_payload', 0, 2, 2).
python_method('RegistryService', 'commands_payload', 0, 2, 2).
python_method('RegistryService', 'uris_payload', 0, 2, 3).
python_method('RegistryService', 'mqtt_status', 0, 2, 2).
python_method('RegistryService', '_generate_ir', 0, 5, 11).
python_method('RegistryService', '_publish_mqtt', 0, 5, 7).
python_class('src/env2llm/sources.py', 'EnvironmentSources').
python_method('EnvironmentSources', 'example_profile', 2, 7, 0).
python_method('EnvironmentSources', 'platform_config', 1, 5, 0).
python_method('EnvironmentSources', 'services_snapshot', 1, 12, 0).
python_class('src/env2llm/sources.py', 'DefaultEnvironmentSources').
python_method('DefaultEnvironmentSources', 'example_profile', 2, 7, 5).
python_method('DefaultEnvironmentSources', 'platform_config', 1, 5, 5).
python_method('DefaultEnvironmentSources', 'services_snapshot', 1, 12, 5).
python_class('src/env2llm/transport/mqtt.py', 'MqttRegistryBridge').
python_method('MqttRegistryBridge', '__init__', 0, 11, 8).
python_method('MqttRegistryBridge', 'topic', 1, 3, 2).
python_method('MqttRegistryBridge', 'connect', 0, 1, 2).
python_method('MqttRegistryBridge', 'disconnect', 0, 1, 2).
python_method('MqttRegistryBridge', 'publish_registry', 2, 1, 3).
python_method('MqttRegistryBridge', 'publish_desktop', 2, 1, 3).
python_method('MqttRegistryBridge', 'publish_event', 3, 1, 3).
python_method('MqttRegistryBridge', 'subscribe_refresh', 1, 1, 1).
python_method('MqttRegistryBridge', '_publish', 2, 2, 2).
python_method('MqttRegistryBridge', '_on_connect', 5, 2, 1).
python_method('MqttRegistryBridge', '_on_message', 3, 9, 7).
python_class('tests/test_mqtt.py', '_FakeClient').
python_method('_FakeClient', '__init__', 0, 1, 0).
python_method('_FakeClient', 'username_pw_set', 2, 1, 0).
python_method('_FakeClient', 'connect', 3, 1, 0).
python_method('_FakeClient', 'loop_start', 0, 1, 0).
python_method('_FakeClient', 'loop_stop', 0, 1, 0).
python_method('_FakeClient', 'disconnect', 0, 1, 0).
python_method('_FakeClient', 'publish', 4, 1, 1).
python_method('_FakeClient', 'subscribe', 2, 1, 1).

% ── Dependencies ─────────────────────────────────────────

% ── Makefile Targets ─────────────────────────────────────
makefile_target('CYAN', 'Colors').
makefile_target('GREEN', '').
makefile_target('YELLOW', '').
makefile_target('RED', '').
makefile_target('RESET', '').
makefile_target('help', '').
makefile_target('install', '').
makefile_target('install-dev', '').
makefile_target('install-ai', '').
makefile_target('setup', '').
makefile_target('env', '').
makefile_target('run', '').
makefile_target('web', '').
makefile_target('shell', '').
makefile_target('plan', '').
makefile_target('execute', '').
makefile_target('examples', '').
makefile_target('run-intent', 'Run with custom package file: make run-intent FILE=path/to/iterun.yaml').
makefile_target('test', '').
makefile_target('test-shell', '').
makefile_target('test-web', '').
makefile_target('test-ai', '').
makefile_target('test-cov', '').
makefile_target('ollama-start', '').
makefile_target('ollama-pull', '').
makefile_target('ollama-models', '').
makefile_target('ollama-status', '').
makefile_target('lint', '').
makefile_target('format', '').
makefile_target('clean', '').
makefile_target('docker-clean', '').
makefile_target('docker-ps', '').
makefile_target('docker-stop', '').
makefile_target('dev', '').
makefile_target('new-intent', '').
makefile_target('show-config', '').

% ── Taskfile Tasks ───────────────────────────────────────

% ── Environment Variables ────────────────────────────────
env_variable('OPENROUTER_API_KEY', '*(not set)*', 'Required: OpenRouter API key (https://openrouter.ai/keys)').
env_variable('LLM_MODEL', 'openrouter/qwen/qwen3-coder-next', 'Model (default: openrouter/qwen/qwen3-coder-next)').
env_variable('PFIX_AUTO_APPLY', 'true', 'true = apply fixes without asking').
env_variable('PFIX_AUTO_INSTALL_DEPS', 'true', 'true = auto pip/uv install').
env_variable('PFIX_AUTO_RESTART', 'false', 'true = os.execv restart after fix').
env_variable('PFIX_MAX_RETRIES', '3', '').
env_variable('PFIX_DRY_RUN', 'false', '').
env_variable('PFIX_ENABLED', 'true', '').
env_variable('PFIX_GIT_COMMIT', 'false', 'true = auto-commit fixes').
env_variable('PFIX_GIT_PREFIX', 'pfix:', 'commit message prefix').
env_variable('PFIX_CREATE_BACKUPS', 'false', 'false = disable .pfix_backups/ directory').

% ── TestQL Scenarios ─────────────────────────────────────
testql_scenario('generated-cli-tests.testql.toon.yaml', 'cli').
testql_scenario('generated-from-pytests.testql.toon.yaml', 'integration').

% ── Semantic Facts from SUMD.md ──────────────────────────
sumd_declared_file('app.doql.less', 'doql').
sumd_declared_file('testql-scenarios/generated-cli-tests.testql.toon.yaml', 'testql').
sumd_declared_file('testql-scenarios/generated-from-pytests.testql.toon.yaml', 'testql').
sumd_declared_file('project/map.toon.yaml', 'analysis').
sumd_declared_file('project/logic.pl', 'analysis').
sumd_declared_file('project/calls.toon.yaml', 'analysis').
sumd_interface('cli', 'argparse').
sumd_interface('cli', '').
sumd_workflow('install', 'manual').
sumd_workflow_step('install', 1, '$(PIP) install -r requirements.txt').
sumd_workflow('install-dev', 'manual').
sumd_workflow_step('install-dev', 1, '$(PIP) install pytest pytest-asyncio httpx anyio').
sumd_workflow('install-ai', 'manual').
sumd_workflow_step('install-ai', 1, '$(PIP) install litellm').
sumd_workflow('setup', 'manual').
sumd_workflow_step('setup', 1, 'echo "$(GREEN)✓ Setup complete$(RESET)"').
sumd_workflow('env', 'manual').
sumd_workflow_step('env', 1, 'if [ ! -f .env ]').
sumd_workflow_step('env', 2, 'cp .env.example .env').
sumd_workflow_step('env', 3, 'echo "$(GREEN)✓ Created .env from .env.example$(RESET)"').
sumd_workflow_step('env', 4, 'else \').
sumd_workflow_step('env', 5, 'echo "$(YELLOW)⚠ .env already exists$(RESET)"').
sumd_workflow_step('env', 6, 'fi').
sumd_workflow('run', 'manual').
sumd_workflow('web', 'manual').
sumd_workflow_step('web', 1, 'echo "$(CYAN)Starting web server on http://$(HOST):$(PORT)$(RESET)"').
sumd_workflow_step('web', 2, '$(PYTHON) -m web.app').
sumd_workflow('shell', 'manual').
sumd_workflow_step('shell', 1, 'echo "$(CYAN)Starting interactive shell$(RESET)"').
sumd_workflow_step('shell', 2, '$(PYTHON) -m cli.main').
sumd_workflow('plan', 'manual').
sumd_workflow_step('plan', 1, '$(PYTHON) -m cli.main plan examples/01-user-api/generated/iterun.yaml -o examples/01-user-api/generated/').
sumd_workflow('execute', 'manual').
sumd_workflow_step('execute', 1, 'ITERUN_EXECUTE=1 ./examples/01-user-api/run.sh').
sumd_workflow('examples', 'manual').
sumd_workflow_step('examples', 1, './examples/run-all.sh').
sumd_workflow('run-intent', 'manual').
sumd_workflow_step('run-intent', 1, 'if [ -z "$(FILE)" ]').
sumd_workflow_step('run-intent', 2, 'echo "$(RED)ERROR: FILE not specified$(RESET)"').
sumd_workflow_step('run-intent', 3, 'echo "Usage: make run-intent FILE=path/to/iterun.yaml"').
sumd_workflow_step('run-intent', 4, 'exit 1').
sumd_workflow_step('run-intent', 5, 'fi').
sumd_workflow_step('run-intent', 6, '$(PYTHON) -m cli.main execute $(FILE)').
sumd_workflow('test', 'manual').
sumd_workflow_step('test', 1, '$(PYTHON) -m pytest tests/ -v').
sumd_workflow('test-shell', 'manual').
sumd_workflow_step('test-shell', 1, '$(PYTHON) -m pytest tests/e2e/test_shell.py -v').
sumd_workflow('test-web', 'manual').
sumd_workflow_step('test-web', 1, '$(PYTHON) -m pytest tests/e2e/test_web.py -v').
sumd_workflow('test-ai', 'manual').
sumd_workflow_step('test-ai', 1, '$(PYTHON) -m pytest tests/e2e/test_ai_gateway.py -v').
sumd_workflow('test-cov', 'manual').
sumd_workflow_step('test-cov', 1, '$(PYTHON) -m pytest tests/ -v --cov=. --cov-report=html --cov-report=term').
sumd_workflow('ollama-start', 'manual').
sumd_workflow_step('ollama-start', 1, 'echo "$(CYAN)Starting Ollama server...$(RESET)"').
sumd_workflow_step('ollama-start', 2, 'ollama serve &').
sumd_workflow_step('ollama-start', 3, 'sleep 2').
sumd_workflow_step('ollama-start', 4, 'echo "$(GREEN)✓ Ollama server started$(RESET)"').
sumd_workflow('ollama-pull', 'manual').
sumd_workflow_step('ollama-pull', 1, 'echo "$(CYAN)Pulling model: $(DEFAULT_MODEL)$(RESET)"').
sumd_workflow_step('ollama-pull', 2, 'ollama pull $(DEFAULT_MODEL)').
sumd_workflow_step('ollama-pull', 3, 'echo "$(GREEN)✓ Model $(DEFAULT_MODEL) ready$(RESET)"').
sumd_workflow('ollama-models', 'manual').
sumd_workflow_step('ollama-models', 1, 'echo ""').
sumd_workflow_step('ollama-models', 2, 'echo "$(CYAN)Recommended Ollama models (≤12B):$(RESET)"').
sumd_workflow_step('ollama-models', 3, 'echo "  $(GREEN)llama3.2$(RESET)       - 3B  - Default, fast"').
sumd_workflow_step('ollama-models', 4, 'echo "  llama3.2:1b    - 1B  - Ultra lightweight"').
sumd_workflow_step('ollama-models', 5, 'echo "  llama3.1:8b    - 8B  - Balanced"').
sumd_workflow_step('ollama-models', 6, 'echo "  mistral        - 7B  - Fast inference"').
sumd_workflow_step('ollama-models', 7, 'echo "  mistral-nemo   - 12B - Best quality"').
sumd_workflow_step('ollama-models', 8, 'echo "  gemma2         - 9B  - Google Gemma 2"').
sumd_workflow_step('ollama-models', 9, 'echo "  phi3           - 3.8B - Microsoft Phi-3"').
sumd_workflow_step('ollama-models', 10, 'echo "  qwen2.5        - 7B  - Alibaba Qwen"').
sumd_workflow_step('ollama-models', 11, 'echo "  codellama      - 7B  - Code generation"').
sumd_workflow_step('ollama-models', 12, 'echo ""').
sumd_workflow_step('ollama-models', 13, 'echo "$(YELLOW)Install:$(RESET) ollama pull <model>"').
sumd_workflow_step('ollama-models', 14, 'echo ""').
sumd_workflow('ollama-status', 'manual').
sumd_workflow_step('ollama-status', 1, 'echo "$(CYAN)Checking Ollama status...$(RESET)"').
sumd_workflow_step('ollama-status', 2, 'curl -s http://localhost:11434/api/tags > /dev/null 2>&1 && \').
sumd_workflow_step('ollama-status', 3, 'echo "$(GREEN)✓ Ollama is running$(RESET)" || \').
sumd_workflow_step('ollama-status', 4, 'echo "$(RED)✗ Ollama is not running$(RESET)"').
sumd_workflow('lint', 'manual').
sumd_workflow_step('lint', 1, 'which ruff > /dev/null 2>&1 && ruff check . || echo "$(YELLOW)ruff not installed$(RESET)"').
sumd_workflow('format', 'manual').
sumd_workflow_step('format', 1, 'which ruff > /dev/null 2>&1 && ruff format . || echo "$(YELLOW)ruff not installed$(RESET)"').
sumd_workflow('clean', 'manual').
sumd_workflow_step('clean', 1, 'echo "$(CYAN)Cleaning...$(RESET)"').
sumd_workflow_step('clean', 2, 'rm -rf __pycache__ */__pycache__ */*/__pycache__').
sumd_workflow_step('clean', 3, 'rm -rf .pytest_cache */.pytest_cache').
sumd_workflow_step('clean', 4, 'rm -rf *.egg-info .eggs').
sumd_workflow_step('clean', 5, 'rm -rf htmlcov .coverage').
sumd_workflow_step('clean', 6, 'rm -rf /tmp/intent-*').
sumd_workflow_step('clean', 7, 'echo "$(GREEN)✓ Cleaned$(RESET)"').
sumd_workflow('docker-clean', 'manual').
sumd_workflow_step('docker-clean', 1, 'echo "$(CYAN)Cleaning Docker resources...$(RESET)"').
sumd_workflow_step('docker-clean', 2, '-docker ps -a --filter "name=$(CONTAINER_PREFIX)-" -q | xargs -r docker rm -f').
sumd_workflow_step('docker-clean', 3, '-docker images --filter "reference=$(CONTAINER_PREFIX)-*" -q | xargs -r docker rmi -f').
sumd_workflow_step('docker-clean', 4, 'echo "$(GREEN)✓ Docker cleaned$(RESET)"').
sumd_workflow('docker-ps', 'manual').
sumd_workflow_step('docker-ps', 1, 'docker ps --filter "name=$(CONTAINER_PREFIX)-"').
sumd_workflow('docker-stop', 'manual').
sumd_workflow_step('docker-stop', 1, 'docker ps --filter "name=$(CONTAINER_PREFIX)-" -q | xargs -r docker stop').
sumd_workflow_step('docker-stop', 2, 'echo "$(GREEN)✓ Containers stopped$(RESET)"').
sumd_workflow('dev', 'manual').
sumd_workflow_step('dev', 1, 'uvicorn web.app:app --reload --host $(HOST) --port $(PORT)').
sumd_workflow('new-intent', 'manual').
sumd_workflow_step('new-intent', 1, '$(PYTHON) -m cli.main new').
sumd_workflow('show-config', 'manual').
sumd_workflow_step('show-config', 1, 'echo ""').
sumd_workflow_step('show-config', 2, 'echo "$(CYAN)Current Configuration:$(RESET)"').
sumd_workflow_step('show-config', 3, 'echo "  HOST=$(HOST)"').
sumd_workflow_step('show-config', 4, 'echo "  PORT=$(PORT)"').
sumd_workflow_step('show-config', 5, 'echo "  DEFAULT_MODEL=$(DEFAULT_MODEL)"').
sumd_workflow_step('show-config', 6, 'echo "  CONTAINER_PORT=$(CONTAINER_PORT)"').
sumd_workflow_step('show-config', 7, 'echo "  CONTAINER_PREFIX=$(CONTAINER_PREFIX)"').
sumd_workflow_step('show-config', 8, 'echo "  OLLAMA_BASE_URL=$(OLLAMA_BASE_URL)"').
sumd_workflow_step('show-config', 9, 'echo "  SKIP_ITERUN_CONFIRMATION=$(SKIP_ITERUN_CONFIRMATION)"').
sumd_workflow_step('show-config', 10, 'echo ""').

