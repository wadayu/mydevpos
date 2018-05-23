#coding:utf-8
'''
ad-hoc模式
'''
__author__ = 'WangDy'
__date__ = '2018/5/21 15:07'

from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.plugins.callback import CallbackBase

#InvertoryManager类
loader = DataLoader()
inventory = InventoryManager(loader=loader,sources=['imoocc_hosts'])
#host = inventory.get_host('192.168.19.130')

#VariableManager类
variable_manager = VariableManager(loader=loader,inventory=inventory)
#variable_manager.get_vars() #获取所以的主机
#variable_manager.get_vars(host=host) #获取指定的主机

#variable_manager.set_host_variable(host,'ansible_ssh_user','wangdaoyun')
#var = variable_manager.get_vars(host=host)
#variable_manager.extra_vars={'myname':'zhidianlife'} 
#var1 = variable_manager.get_vars(host=host)
#print var1

#Options执行选项
Options = namedtuple('Options',
                     ['connection',
                      'remote_user',
                      'ask_sudo_pass',
                      'verbosity',
                      'ack_pass',
                      'module_path',
                      'forks',
                      'become',
                      'become_method',
                      'become_user',
                      'check',
                      'listhosts',
                      'listtasks',
                      'listtags',
                      'syntax',
                      'sudo_user',
                      'sudo',
                      'diff',])
options = Options(connection='smart',
                       remote_user=None,
                       ack_pass=None,
                       sudo_user=None,
                       forks=5,
                       sudo=False,
                       ask_sudo_pass=None,
                       verbosity=5,
                       module_path=None,
                       become=True,
                       become_method='sudo',
                       become_user='root',
                       check=False,
                       diff=False,
                       listhosts=None,
                       listtasks=None,
                       listtags=None,
                       syntax=None,)

#Play执行对象和模块
play_source = dict(
	name = 'Ansible Play ad-hoc test',
	hosts = '192.168.19.130',
	gather_facts = 'no',
	tasks = [
	    dict(action=dict(module='shell',args='touch /tmp/ad_hoc_test'))
	    # dict(action=dict(module='debug', args=dict(msg='{{shell_out.stdout}}')))
	]
)
play = Play().load(play_source,variable_manager=variable_manager,loader=loader)

class ModelResultsCollector(CallbackBase):
    """
    重写callbackBase类的部分方法
    """
    def __init__(self, *args, **kwargs):
        super(ModelResultsCollector, self).__init__(*args, **kwargs)
        self.host_ok = {}
        self.host_unreachable = {}
        self.host_failed = {}
    def v2_runner_on_unreachable(self, result):
        self.host_unreachable[result._host.get_name()] = result
    def v2_runner_on_ok(self, result):
        self.host_ok[result._host.get_name()] = result
    def v2_runner_on_failed(self, result,ignore_errors=False):
        self.host_failed[result._host.get_name()] = result

callback =  ModelResultsCollector()

passwords = dict()
tqm = TaskQueueManager(
	inventory = inventory,
	variable_manager = variable_manager,
	loader = loader,
	options = options,
	passwords = passwords,
	stdout_callback = callback,	
)

tqm.run(play)

#print callback.host_ok.items()
result_raw = {'success':{},'failed':{},'unreachable':{}}
for host,result in callback.host_ok.items():
    result_raw['success'][host] = result._result
for host,result in callback.host_failed.items():
    result_raw['failed'][host] = result._result
for host,result in callback.host_unreachable.items():
    result_raw['unreachable'][host] = result._result

print result_raw
