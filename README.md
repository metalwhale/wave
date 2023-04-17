# wave
K8s cluster for Whale

## Initial setup
Create a virtual environment:
```
sudo apt-get install -y python3-pip
pip3 install -U virtualenv
virtualenv --python=$(which python3) ansible
source ansible/bin/activate
```

Install requirements for `kubespray` ([reference](https://github.com/kubernetes-sigs/kubespray/blob/master/docs/ansible.md#installing-ansible)):
```
cd kubernetes/kubespray/
pip install -U -r requirements-2.12.txt
cd ../../
```

## Deploy kubernetes cluster
```
cd kubernetes/kubespray/
ansible-playbook -i ../inventory --become --become-user=root --ask-become-pass cluster.yml
cd ../../
```
