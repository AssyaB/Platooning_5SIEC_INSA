using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.Net.Sockets;

namespace UIGeiCar___Nairobi
{
    public partial class UIGeiCar : Form
    {
        TcpClient clientSocket = new TcpClient();
        NetworkStream nwStream;
        Boolean bConnected = false;
        Boolean platooning_mode = false;
        Boolean waiting_mode = false;

        public UIGeiCar()
        {
            InitializeComponent();
        }
        

        private void Bconnect_Click(object sender, EventArgs e)
        {
            try
            {
                clientSocket.Connect(ip.Text, 6666);
                bconnect.Text = "Connected";
                bconnect.Enabled = false;
                nwStream = clientSocket.GetStream();
                bConnected = true;
                EnableAll();
                ip.Enabled = false;
                Receive();
            }
            catch (SocketException ex)
            {
                bConnected = false;
                bconnect.Text = "Failed to connect";
                Console.WriteLine(ex.Message);
            }
        }

        private void EnableAll()
        {
            bforward.Enabled = true;
            bright.Enabled = true;
            SpdBar.Enabled = true;
            bleft.Enabled = true;
            bbackward.Enabled = true;
            bstopMOV.Enabled = true;
            bstopSTE.Enabled = true;
        }

        private void DisableAll()
        {
            bforward.Enabled = false;
            bright.Enabled = false;
            SpdBar.Enabled = false;
            bleft.Enabled = false;
            bbackward.Enabled = false;
            bstopMOV.Enabled = false;
            bstopSTE.Enabled = false;
        }

        async void Receive()
        {
            int cmpt = 0;
            if (bConnected) { 
                while (clientSocket.Connected)
                {
                    byte[] myReadBuffer = new byte[2048];
                    await nwStream.ReadAsync(myReadBuffer, 0, myReadBuffer.Length);
                    String st = Encoding.UTF8.GetString(myReadBuffer);
                    String[] msgs = st.Split(';');

                    foreach (String msg in msgs)
                    {
                        Console.WriteLine(msg);
                        String[] elt = msg.Split(':');
                        switch (elt[0])
                        {
                            /*case "UFL":
                                eUSFL.Text = elt[1];
                                break;
                            case "UFC":
                                eUSFC.Text = elt[1];
                                break;
                            case "UFR":
                                eUSFR.Text = elt[1];
                                break;
                            case "URL":
                                eUSRL.Text = elt[1];
                                break;
                            case "URC":
                                eUSRC.Text = elt[1];
                                break;
                            case "URR":
                                eUSRR.Text = elt[1];
                                break;
                            case "POS":
                                ePOS.Text = elt[1];
                                break;
                            case "BAT":
                                eBAT.Text = elt[1];
                                break;
                            case "SWL":
                                eSPL.Text = elt[1];
                                break;
                            case "SWR":
                                eSPR.Text = elt[1];
                                break;*/
                            case "YAW":
                                eYAW.Text = elt[1];
                                break;
                            case "ROL":
                                eROL.Text = elt[1];
                                break;
                            case "PIT":
                                ePITCH.Text = elt[1];
                                break;
                            case "LID":
                                eLIDAR.Text = elt[1];
                                break;
                            default:
                                cmpt = (cmpt + 1) % 100;
                                break;
                        }
                        if (cmpt == 0)
                        {
                            switch (elt[0])
                            {
                                case "UFL":
                                    eUSFL.Text = elt[1];
                                    break;
                                case "UFC":
                                    eUSFC.Text = elt[1];
                                    break;
                                case "UFR":
                                    eUSFR.Text = elt[1];
                                    break;
                                case "URL":
                                    eUSRL.Text = elt[1];
                                    break;
                                case "URC":
                                    eUSRC.Text = elt[1];
                                    break;
                                case "URR":
                                    eUSRR.Text = elt[1];
                                    break;
                                case "POS":
                                    ePOS.Text = elt[1];
                                    break;
                                case "BAT":
                                    eBAT.Text = elt[1];
                                    break;
                                case "SWL":
                                    eSPL.Text = elt[1];
                                    break;
                                case "SWR":
                                    eSPR.Text = elt[1];
                                    break;
                            }
                        }
                    }
                }
            }
        }

        private void Bright_Click(object sender, EventArgs e)
        {
            if (bConnected)
            {
                byte[] bytes = Encoding.ASCII.GetBytes("STE:" + "right;");
                nwStream.Write(bytes, 0, bytes.Length);
            }
        }

        private void Bbackward_Click(object sender, EventArgs e)
        {
            if (bConnected)
            {
                byte[] bytes = Encoding.ASCII.GetBytes("MOV:" + "backward;");
                nwStream.Write(bytes, 0, bytes.Length);
            }
        }

        private void Bleft_Click(object sender, EventArgs e)
        {
            if (bConnected)
            {
                byte[] bytes = Encoding.ASCII.GetBytes("STE:" + "left;");
                nwStream.Write(bytes, 0, bytes.Length);
            }
        }

        private void Bforward_Click(object sender, EventArgs e)
        {
            if (bConnected)
            {
                byte[] bytes = Encoding.ASCII.GetBytes("MOV:" + "forward;");
                nwStream.Write(bytes, 0, bytes.Length);
            }
        }

        private void BstopSTE_Click(object sender, EventArgs e)
        {
            if (bConnected)
            {
                byte[] bytes = Encoding.ASCII.GetBytes("STE:" + "stop;");
                nwStream.Write(bytes, 0, bytes.Length);
            }
        }

        private void BstopMOV_Click(object sender, EventArgs e)
        {
            if (bConnected)
            {
                byte[] bytes = Encoding.ASCII.GetBytes("MOV:" + "stop;");
                nwStream.Write(bytes, 0, bytes.Length);
            }
        }
        
        private void UIGeiCar_KeyDown(object sender, KeyEventArgs e)
        {
            byte[] bytes = Encoding.ASCII.GetBytes("STE:" + "stop;");
            if (bConnected)
            {
                switch (e.KeyCode)
                {
                    case Keys.Down:
                        bytes = Encoding.ASCII.GetBytes("MOV:" + "backward;");
                        break;
                    case Keys.Up:
                        bytes = Encoding.ASCII.GetBytes("MOV:" + "forward;");
                        break;
                    case Keys.Left:
                        bytes = Encoding.ASCII.GetBytes("STE:" + "left;");
                        break;
                    case Keys.Right:
                        bytes = Encoding.ASCII.GetBytes("STE:" + "right;");
                        break;
                }
                nwStream.Write(bytes, 0, bytes.Length);
            }
        }

        private void UIGeiCar_KeyUp(object sender, KeyEventArgs e)
        {
            byte[] bytes = Encoding.ASCII.GetBytes("STE:" + "stop;");
            if (bConnected)
            {
                switch (e.KeyCode)
                {
                    case Keys.Down:
                    case Keys.Up:
                        bytes = Encoding.ASCII.GetBytes("MOV:" + "stop;");
                        break;
                    case Keys.Left:
                    case Keys.Right:
                        bytes = Encoding.ASCII.GetBytes("STE:" + "stop;");
                        break;
                }
                nwStream.Write(bytes, 0, bytes.Length);
            }
        }

        private void UIGeiCar_FormClosing(object sender, FormClosingEventArgs e)
        {
            Application.Exit();
        }

        private void SpdBar_ValueChanged(object sender, EventArgs e)
        {
            byte[] bytes = Encoding.ASCII.GetBytes("SPE:" + SpdBar.Value.ToString() + ";");
            nwStream.Write(bytes, 0, bytes.Length);
            eSPD.Text = SpdBar.Value.ToString();
        }

        private void KbCtrl_PreviewKeyDown(object sender, PreviewKeyDownEventArgs e)
        {
            byte[] bytes = Encoding.ASCII.GetBytes("STE:" + "stop;");
            if (bConnected)
            {
                switch (e.KeyCode)
                {
                    case Keys.Down:
                        bytes = Encoding.ASCII.GetBytes("MOV:" + "backward;");
                        break;
                    case Keys.Up:
                        bytes = Encoding.ASCII.GetBytes("MOV:" + "forward;");
                        break;
                    case Keys.Left:
                        bytes = Encoding.ASCII.GetBytes("STE:" + "left;");
                        break;
                    case Keys.Right:
                        bytes = Encoding.ASCII.GetBytes("STE:" + "right;");
                        break;
                }
                nwStream.Write(bytes, 0, bytes.Length);
            }
        }

        private void BmodePlatooning_Click(object sender, EventArgs e)
        {
            if (bConnected)
            {
                if (platooning_mode == false && waiting_mode == false)
                {
                    byte[] bytes = Encoding.ASCII.GetBytes("PLA:" + "on;");
                    BmodePlatooning.BackgroundImage = Properties.Resources.wait;
                    nwStream.Write(bytes, 0, bytes.Length);
                    platooning_mode = false;
                    waiting_mode = true;
                    ILIDAR.Visible = true;
                    eLIDAR.Visible = true;
                    BPlat_accept.Enabled = true;
                    BPlat_refuse.Enabled = true;
                    BPlat_accept.Visible = true;
                    BPlat_refuse.Visible = true;
                    //BmodePlatooning.BackgroundImageLayout =;
                }
                else
                {
                    if(platooning_mode == true || waiting_mode == true)
                    {
                        byte[] bytes = Encoding.ASCII.GetBytes("PLA:" + "off;");
                        BmodePlatooning.BackgroundImage = Properties.Resources.OFF;
                        nwStream.Write(bytes, 0, bytes.Length);
                        platooning_mode = false;
                        waiting_mode = false;
                        ILIDAR.Visible = false;
                        eLIDAR.Visible = false;
                        BPlat_accept.Enabled = false;
                        BPlat_refuse.Enabled = false;
                        BPlat_accept.Visible = false;
                        BPlat_refuse.Visible = false;
                    }
                }

            }
        }

        private void Bdisconnect_Click(object sender, EventArgs e)
        {
            try
            {
                clientSocket.Close();
                bconnect.Enabled = true;
                bdisconnect.Enabled = false;
                bConnected = false;
                ip.Enabled = true;
                DisableAll();
            }
            catch (SocketException ex)
            {
                bConnected = true;
                bconnect.Text = "Failed to disconnect";
                Console.WriteLine(ex.Message);
            }
        }

        private void BPlat_accept_Click(object sender, EventArgs e)
        {
            if (waiting_mode == true)
            {
                byte[] bytes = Encoding.ASCII.GetBytes("PLA:" + "yes;");
                BmodePlatooning.BackgroundImage = Properties.Resources.ON;
                nwStream.Write(bytes, 0, bytes.Length);
                waiting_mode = false;
                platooning_mode = true;
                ILIDAR.Visible = true;
                eLIDAR.Visible = true;
                BPlat_accept.Enabled = false;
                BPlat_refuse.Enabled = false;
                BPlat_accept.Visible = false;
                BPlat_refuse.Visible = false;
            }
        }

        private void BPlat_refuse_Click(object sender, EventArgs e)
        {
            if (waiting_mode == true)
            {
                byte[] bytes = Encoding.ASCII.GetBytes("PLA:" + "no;");
                BmodePlatooning.BackgroundImage = Properties.Resources.wait;
                nwStream.Write(bytes, 0, bytes.Length);
                ILIDAR.Visible = true;
                eLIDAR.Visible = true;
                BPlat_accept.Enabled = true;
                BPlat_refuse.Enabled = true;
                BPlat_accept.Visible = true;
                BPlat_refuse.Visible = true;
            }
        }
    }
}
