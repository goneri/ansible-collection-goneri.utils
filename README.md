# A collection of tools for Ansible

## Collect the task results

Install the `goneri.utils` collection and define the following environment variables:

- `ANSIBLE_CALLBACK_WHITELIST`: Ask Ansible to load the callback plugin.
- `COLLECT_TASK_OUTPUTS_COLLECTION`: Specify the name of the collection.
- `COLLECT_TASK_OUTPUTS_TARGET_DIR`: Target directory where to write the results.

```shell
export ANSIBLE_CALLBACK_WHITELIST=goneri.utils.collect_task_outputs
export COLLECT_TASK_OUTPUTS_COLLECTION=vmware.vmware_rest
export COLLECT_TASK_OUTPUTS_TARGET_DIR=$(realpath ../../../../docs/source/vmware_rest_scenarios/task_outputs/)
```

You can now run you playbook:

```shell
ansible-playbook playbook.yaml
```

## inject_RETURN

You can use the result to update the  [RETURN sections](https://docs.ansible.com/ansible/latest/dev_guide/developing_modules_documenting.html#documentation-block) of your modules
?

### Usage

```shell
./scripts/inject_RETURN.py ~/.ansible/collections/ansible_collections/vmware/vmware_rest/docs/source/vmware_rest_scenarios/task_outputs/ ~/git_repos/ansible-collections/vmware_rest/ --config-file config/inject_RETURN.yaml
```

# To summarize the benefit

- always keep the RETURN block up to date.
- easier to spot the case when the module output get changed by new change.
