# A collection of tools for Ansible

## update_return_section

- Do you write Ansible modules?
- Do you need to maintain all these [RETURN sections](https://docs.ansible.com/ansible/latest/dev_guide/developing_modules_documenting.html#documentation-block)?
- Are you lazy and feel like this should be automated!?
- So am I!... And you may like `update_return_section`!

`update_return_section` is callback plugin that will:

- collect the output of the tasks
- compare it with the existing RETURN block
- if the new block is longer, it will inject it in the `RETURN` section

oh also, THIS CALLBACK WILL REWRITE THE CONTENT OF YOUR MODULES BEHIND YOUR BACK. So ensure your work environment is safe before using it.

## To summarize the benefit

- always keep the RETURN block up to date.
- easier to spot the case when the module output get changed by new change.

## Installation

```shell
mkdir ~/.ansible/collections/ansible_collections/goneri
git clone https://github.com/goneri/ansible-collection-goneri.utils  ~/.ansible/collections/ansible_collections/goneri/utils
```

## Configuration

Add a `update_return_section.yml` in your collection's `meta` directory.

```yaml
---
enabled: true
keys:
# write a specific description for the id key (optional)
  id:
    description: moid of the resource
```

### Usage

Frankly, it's rather simple :-)

```shell:
ANSIBLE_CALLBACK_WHITELIST=goneri.utils.update_return_section
ansible-playbook playbook.yaml
```
