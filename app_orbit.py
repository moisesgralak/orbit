import tkinter as tk
from tkinter import font as tkfont
from tkinter import StringVar
import json
from time import sleep
import subprocess
import serial, sys


with open('listaloco.json', 'r') as f:
    lista = json.load(f)


class ConfigOrbit(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.fontetit = tkfont.Font(family='Helvetica', size='15', weight='bold')
        self.fontedef = tkfont.Font(family='Helvetica', size='12')
        self.fontebt = tkfont.Font(family='Helvetica', size=12, weight='bold')
        self.label_titulo = tk.Label(self, text="Bem vindo ao script de configuração dos rádios orbit para locomotiva.",
                                     font=self.fontetit)
        self.label_titulo.pack(pady=20)

        self.lfbackup = tk.LabelFrame(self, text='Script para configurações de fábrica', width=900, height=100,
                                 font=self.fontebt, bd=5)
        self.lfbackup.pack(side='top', fill='x', padx=50, pady=15)

        self.lbbackup = tk.Label(self.lfbackup, text='Conecte o cabo na porta COM ou USB do radio para executar o '
                                                     'backup das configurações do radio', font=self.fontedef)
        self.lbbackup.pack(side='left', padx=10, pady=5)

        self.btbackup = tk.Button(self.lfbackup, text='Reset', font=self.fontetit, width=10,
                                  command=lambda: botao_backup())

        self.lf1 = tk.LabelFrame(self, text='Script para configurações de fábrica', width=900, height=100,
                                 font=self.fontebt, bd=5)
        self.lf1.pack(side='top', fill='x', padx=50, pady=15)
        self.lbtxt = tk.Label(self.lf1, text='Conecte o cabo na porta COM ou USB do radio para executar a configuração'
                                             ' de padrões de fábrica do rádio.', font=self.fontedef)
        self.lbtxt.pack(side='left', padx=10, pady=5)
        self.btfd = tk.Button(self.lf1, text='Reset', font=self.fontetit, width=10,
                              command=lambda: botao_reset())
        self.btfd.pack(padx=10, pady=5, after=self.lbtxt)

        self.lf2 = tk.LabelFrame(self, text='Configurações do rádio', width=900, height=600,
                                 font=('Arial', 12, 'bold'), bd=5)
        self.lf2.pack(side='top', fill='x', padx=50, pady=15)

        self.lbloco = tk.Label(self.lf2, text='Digite o numero da Locomotiva: ', font=self.fontedef)
        self.lbloco.pack(side='left', padx=10)

        self.entloco = tk.Entry(self.lf2, width=20, font=self.fontedef)
        self.entloco.pack(side='left', pady=10)

        self.btvalida = tk.Button(self.lf2, text='Validar locomotiva', font=self.fontebt, width=15,
                                  command=lambda : testaid(self.entloco.get()))
        self.btvalida.pack(side='left', padx=10, pady=10)

        self.btconfig = tk.Button(self.lf2, text='Configurar', font=self.fontebt, width=15,
                                  command=lambda: botaoconfig(self.entloco.get()))
        self.btconfig.pack(side='left', padx=10, pady=10)

        self.lfsaida = tk.LabelFrame(self, text='Saída de comandos:', font=('Arial', 12, 'bold'), width=900,
                                     height=50, bd=5)
        self.saidacomando = StringVar()

        self.lbsaida = tk.Label(self.lfsaida, textvariable=self.saidacomando, font=self.fontedef)

        self.lfsaida.pack(fill='x', side='top', padx=50, pady=15)
        self.lbsaida.pack(side='left', fill='x', padx=20, pady=5)


        def botao_reset():
            port = "COM18"
            baudRate = 9600
            # Realiza a conexão via Serial atraves da porta COM e o BaudRate configurado
            try:
                ser = serial.Serial(port, baudRate, timeout=1)
                if not ser.isOpen():
                    ser.open()
            except Exception as e:
                print("Error opening com port. Quitting." + str(e))
                sys.exit(0)
            print("Opening " + ser.portstr)

            # Executa as linhas de comando necessárias para fazer o reset
            reset_factory_def = ['admin\r',
                                 'Rumomds2017\r',
                                 'request system recovery rollback snapshot Factory\r',
                                 'yes\r',
                                 'exit\r']
            for dado in reset_factory_def:
                ser.write(dado.encode('utf-8'))
                sleep(0.5)
            ser.close()
            print('closed')

        def configradio(idl, vlo, ipmo):
            port = "COM18"
            baudRate = 9600

            try:
                ser = serial.Serial(port, baudRate, timeout=1)
                if not ser.isOpen():
                    ser.open()
            except Exception as e:
                print("Error opening com port. Quitting." + str(e))
                sys.exit(0)
            print("Opening " + ser.portstr)
            ser.read_until('login:')
            sleep(2)
            user = bytes('admin\r', 'utf-8')
            ser.write(user)
            sleep(2)
            ser.read_until('Password:')
            sleep(2)
            passwd_def = bytes('admin\r', 'utf-8')
            ser.write(passwd_def)
            sleep(2)
            ser.read_until('>')
            sleep(1)
            config_interfaces = ['config\r',
                                 'delete interfaces interface Bridge bridge-settings members port ETH1\r',
                                 'delete interfaces interface Bridge bridge-settings members port LnRadio\r',
                                 'insert interfaces interface VLAN240\r',
                                 'insert interfaces interface VLAN241\r',
                                 'insert interfaces interface VLAN242\r',
                                 'set interfaces interface VLAN240 type vlan vlan-config vlan-id 240\r',
                                 'set interfaces interface VLAN241 type vlan vlan-config vlan-id 241\r',
                                 'set interfaces interface VLAN242 type vlan vlan-config vlan-id 242\r',
                                 'set interfaces interface LnRadio type ln\r',
                                 'set interfaces interface LnRadio enabled true\r',
                                 'set interfaces interface LnRadio vlan-mode trunk\r',
                                 'set interfaces interface LnRadio vlans [ VLAN240 VLAN241 VLAN242 ]\r',
                                 'set interfaces interface LnRadio ln-config\r',
                                 'set interfaces interface LnRadio ln-config virtual-radio-channel LnRadio\r',
                                 'set interfaces interface LnRadio ln-config device-mode remote\r',
                                 'set interfaces interface LnRadio ln-config network-name rumologistica\r',
                                 'set interfaces interface LnRadio ln-config power 37\r',
                                 'set interfaces interface LnRadio ln-config tx-frequency 458.3000\r',
                                 'set interfaces interface LnRadio ln-config rx-frequency 468.3000\r',
                                 'set interfaces interface LnRadio ln-config channel 25KHz-20ksps\r',
                                 'set interfaces interface LnRadio ln-config modulation qpsk\r',
                                 'set interfaces interface LnRadio ln-config fec adaptive-gain\r',
                                 'set interfaces interface LnRadio ln-config security security-mode psk\r',
                                 'set interfaces interface LnRadio ln-config security encryption aes128-ccm\r',
                                 'set interfaces interface LnRadio ln-config security passphrase $4$FerhTQCKRIYPxY9xcJTWQQ==\r',
                                 'set system name loco' + idl + '\r',
                                 'set interfaces interface VLAN240 ipv4 address ' + ipmo + ' prefix-length 21\r',
                                 'set interfaces interface ETH1 type ethernet vlan-mode access vlan VLAN' + vlo + '\r',
                                 'set services dhcp enabled false\r',
                                 'set services snmp agent enabled true\r',
                                 'set services snmp community trilho\r',
                                 'set routing static-routes ipv4 route 10 dest-prefix 0.0.0.0/0 next-hop 10.253.8.1 outgoing-interface VLAN240 preference 10\r',
                                 'set routing static-routes ipv4 route 10 description Rota_default_monitoramento_orbit\r',
                                 'set system authentication password-options minimum-capital-letters 1 minimum-length 6\r',
                                 'request system authentication change-password password Rumomds2017 user admin\r',
                                 'set interfaces interface ETH1 description Orbit-ETH1_to_SAR-HM-Port2\r',
                                 'set interfaces interface VLAN240 description Vlan_monitoramento_orbit\r',
                                 'set interfaces interface VLAN241 description Vlan_producao_orbit\r',
                                 'set interfaces interface VLAN242 description Vlan_producao_orbit\r',
                                 'commit\r',
                                 'yes\r',
                                 'exit\r',
                                 'exit\r']
            for cmd in config_interfaces:
                sleep(2.5)
                ser.write(cmd.encode('utf-8'))
                print(cmd)

            saida = ser.read_all().decode('ascii')
            arq = open('saida.txt', 'a')
            arq.write(saida)
            sleep(2)
            print('Finalizado')
            ser.close()

        def testaid(num):
            lista1 = ['603', '604', '605', '606', '607', '608', '609', '610', '611', '612', '613', '614', '615', '616',
                      '617', '633',
                      '634', '635', '636', '637', '638', '639', '680', '681', '682', '683', '684', '685', '686', '687',
                      '688', '689',
                      '690', '691', '692', '693', '694', '695', '696', '697', '698', '754', '755', '756', '757', '758',
                      '759', '760',
                      '761', '762', '763', '764', '765', '766', '767', '768', '769', '770', '771', '7338', '7339',
                      '7340', '7341',
                      '7342', '7343', '7344', '7345', '7346', '7347', '7349', '7350', '7351', '7352', '8273', '8274',
                      '8275', '8276',
                      '8277', '8278', '8279', '8280', '8281', '8282', '8283', '8284', '8285', '8286', '8287', '8288',
                      '8289', '8290',
                      '8291', '8292', '8293', '8294', '8295', '8296', '8297', '8298', '8299', '8316', '8317', '8318',
                      '8319', '8320',
                      '8321', '8322', '8323', '8324', '8394', '8395', '8396', '8397', '8398', '8399', '8414', '8415',
                      '8416', '8417',
                      '8418', '8419', '8420', '8421', '8422', '8423', '8424', '8425', '8426', '8427', '8428', '9051',
                      '9052', '9053',
                      '9054', '9055', '9056', '9057', '9058', '9059', '9060', '9061', '9062', '9580', '9810', '9811',
                      '9812', '9813',
                      '9814', '9815', '9816', '9817', '9818', '9819', '9820', '9821', '9822', '9823', '9824', '9825',
                      '9826', '9827',
                      '9828', '9829', '9830', '9831', '9832', '9833', '9834', '9835', '9836', '9837', '9838', '9839',
                      '9840', '9841',
                      '9842', '9843', '9844', '9845', '9846', '9847', '9848', '9849', '9850', '9851', '9852', '9853',
                      '9854', '9855',
                      '9856', '9857', '9858', '9859', '9860', '9861', '9862', '9863', '9864', '9865', '9866', '9867',
                      '9868', '9869',
                      '9871', '9872', '9873', '9874', '9875', '9876', '9877', '9878', '9879', '9879', '9880', '9881',
                      '9882', '9883',
                      '9884', '9885', '9886', '9887', '9888', '9889', '9890', '9891', '9892', '9893', '9894', '9895',
                      '9896', '9897',
                      '9898', '9899', '9900', '9901', '9902', '9903', '9904', '9905', '9906', '9907', '9908', '9909',
                      '9910', '9911',
                      '9912', '9913', '9914', '9915', '9916', '9917', '9918', '9919', '9920', '9921', '9922']
            if num is '':
                nulo = 'O ID não pode ser nulo.'
                self.saidacomando.set(nulo)
            elif num not in lista1:
                errado = 'Locomotiva não cadastrada ou inexistente.'
                self.saidacomando.set(errado)
            else:
                self.saidacomando.set('Locomotiva ok!')

        def botao_backup():
            pass

        def botaoconfig(loco):
            self.saidacomando.set('A locomotiva a ser configurada é a '+loco)
            for row in lista['endloco']:

                idl = row['idloco']
                vlo = row['vlanorb']
                ipmo = row['ipmonorb']

                if loco == idl:
                    configradio(idl, vlo, ipmo)
                    break


app = ConfigOrbit()
app.geometry("1024x768")
app.title("Script de configuração rádio Orbit")
app.mainloop()

