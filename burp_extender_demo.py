from burp import IBurpExtender, ITab
from javax import swing;
from java.awt import BorderLayout
import sys, time, threading, socket

class BurpExtender(IBurpExtender, ITab):
    def registerExtenderCallbacks(self,callbacks):
        self.clicked = False
        self.response_data = ""
        self.kill_threads = False

        sys.stdout = callbacks.getStdout()
        self.callbacks = callbacks
        callbacks.setExtensionName("Bind Shell")

        self.tab = swing.JPanel(BorderLayout())

        text_panel = swing.JPanel()
        box_vertical = swing.Box.createVerticalBox()

        box_horizontal = swing.Box.createHorizontalBox()
        self.ip_address = swing.JTextArea("",2,50)
        self.ip_address.setLineWrap(True)
        self.ip_address.border = swing.BorderFactory.createTitledBorder("IP Address:")
        box_horizontal.add(self.ip_address)
        self.port = swing.JTextArea("",2,20)
        self.port.setLineWrap(True)
        self.port.border = swing.BorderFactory.createTitledBorder("Port:")
        box_horizontal.add(self.port)
        box_vertical.add(box_horizontal) 

        box_horizontal= swing.Box.createHorizontalBox()
        self.user_command = swing.JTextArea('',2,50)
        self.user_command.setLineWrap(True)
        self.user_command.border = swing.BorderFactory.createTitledBorder("Command:")
        box_horizontal.add(self.user_command)
        box_vertical.add(box_horizontal)

        box_horizontal = swing.Box.createHorizontalBox()
        button_panel = swing.JPanel()

        self.connect_button = swing.JButton('[--- Connect --- ]', actionPerformed=self.connect)
        self.send_button = swing.JButton("[--- Send ---]", actionPerformed=self.send)
        self.disconnect_button = swing.JButton('[--- Disconnect ---]', actionPerformed=self.disconnect)
        self.send_button.enabled = False
        self.disconnect_button.enabled = False

        button_panel.add(self.connect_button)
        button_panel.add(self.send_button)
        button_panel.add(self.disconnect_button)
        box_horizontal.add(button_panel)
        box_vertical.add(box_horizontal)

        box_horizontal = swing.Box.createHorizontalBox()
        self.output = swing.JTextArea("",20,50)
        self.output.setLineWrap(True)
        self.output.setEditable(False)

        scroll = swing.JScrollPane(self.output)
        box_horizontal.add(scroll)
        box_vertical.add(box_horizontal)



        text_panel.add(box_vertical)
        self.tab.add(text_panel)
    
        callbacks.addSuiteTab(self)
        return

    def connect(self, event):
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.connect((self.ip_address.text,int(self.port.text)))
            self.kill_threads = False

            threading.Thread(target=self.send_thread).start()
            threading.Thread(target=self.recv_thread).start()

            self.connect_button.enabled = False
            self.disconnect_button.enabled = True
            self.send_button.enabled  = True
            self.ip_address.enabled = False
            self.port.enabled = False


            self.output.text = "[+] Connected to {} bindshell".format(self.ip_address.text)
            
        except:
            self.output.text = "[+] Could not connect to {}!, try again!".format(self.ip_address.text)

    
    def send(self, event):
        self.clicked = True
        time.sleep(1)
        self.output.text = self.response_data
    
    def disconnect(self, event):
        self.s.send("exit")
        self.s.close()
        self.kill_threads = True

        self.ip_address.enabled = True
        self.port.enabled = True
        self.connect_button.enabled = True
        self.disconnect_button.enabled = False
        self.send_button.enabled = False
        self.output.text = "[+] Disconnected!"

    def send_thread(self):
        while True:
            if self.kill_threads:
                sys.exit()
            if self.clicked:
                self.clicked = False
                try:
                    self.s.send(self.user_command.text)
                except:
                    self.output.text= "Connection is not reachable"
                    self.kill_threads = True

    def recv_thread(self):
        if self.kill_threads:
            sys.exit()
        data = self.s.recv(4096).replace("Enter Command> ","")
        self.response_data = data

    def getTabCaption(self):
        return "Bind Shell"
    
    def getUiComponent(self):
        return self.tab
    