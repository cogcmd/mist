from mists.commands.ec2 import Base

class ChangeStateCommand(Base):
    def handle_reboot(self):
        if len(self.instances) > 0:
            self.region.reboot_instances(self.instances)
        self.resp.append_body({"instances": self.instances,
                               "region": self.region_name,
                               "action": "rebooted"}, template="state_change")

    def handle_stop(self):
        if len(self.instances) > 0:
            self.region.stop_instances(self.instances)
        self.resp.append_body({"instances": self.instances,
                               "region": self.region_name,
                               "action": "stopped"}, template="state_change")

    def handle_start(self):
        if len(self.instances) > 0:
            self.region.start_instances(self.instances)
        self.resp.append_body({"instances": self.instances,
                               "region": self.region_name,
                               "action": "started"}, template="state_change")

    def usage_error(self):
        self.abort()
        self.response.string("ec2_state --region=<region> [start|stop|rebot] instance1 ...").send()


    def run(self):
        if self.request.args == None or len(self.request.args) < 2:
            self.usage_error()
        self.instances = args[1:]
        self.connect()
        if self.request.args[0] == "reboot":
            self.handle_reboot()
        elif self.request.args[0] == "stop":
            self.handle_stop()
        elif self.request.args[0] == "start":
            self.handle_start()
        else:
            self.usage_error()
