# wave
K8s cluster for Whale

## Initial setup
Create a virtual environment:
```
sudo apt-get install -y python3-pip
pip3 install -U virtualenv
python3 -m virtualenv --python=$(which python3) ansible
source ansible/bin/activate
```

Install requirements for `kubespray` ([reference](https://github.com/kubernetes-sigs/kubespray/blob/master/docs/ansible.md#installing-ansible)):
```
cd kubernetes/kubespray/
pip install -U -r requirements-2.12.txt
cd ../../
```

Install galaxy roles
```
ansible-galaxy install -r requirements.yml
```

## Apply base playbooks
(Assume that bastion is the local host)
```
cd ocean/
ansible-playbook -i inventory.yaml --ask-become-pass base.yml
cd ../
```

## Deploy kubernetes cluster
Apply cluster playbooks:
```
cd kubernetes/kubespray/
ansible-playbook -i ../inventory --become --become-user=root --ask-become-pass cluster.yml
ansible-playbook -i ../inventory --become --become-user=root --ask-become-pass ../custom/cluster.yml
cd ../../
```
Create storage:
```
cd ocean/
ansible-playbook -i inventory.yaml --become --become-user=root --ask-become-pass storage.yml
cd ../
```
