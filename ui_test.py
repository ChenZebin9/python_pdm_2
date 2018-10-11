"""测试wxPython的对话框"""

import sys

sys.path.append('C:/Users/Zebin/OneDrive/Program/Python/wx')

import MainFrame as mf
import wx


class MainWindows(mf.Frame2):
    def __init__(self, parent):
        mf.Frame2.__init__(self, parent)
        # self.m_textCtrl.setValidator(TextObjectValidator())

    def click_on_click(self, event):
        ss = self.m_textCtrl.GetLineText(0)
        wx.MessageBox("你好，{0}".format(ss), "没什么", wx.OK | wx.ICON_INFORMATION)

    def click_on_close_button(self, event):
        self.Close(False)


class TextObjectValidator(wx.PyValidator):
    """ This validator is used to ensure that the user has entered something
        into the text object editor dialog's text field.
    """

    def __init__(self):
        """ Standard constructor.
        """
        wx.PyValidator.__init__(self)

    def Clone(self):
        """ Standard cloner.

            Note that every validator must implement the Clone() method.
        """
        return TextObjectValidator()

    def Validate(self, win):
        """ Validate the contents of the given text control.
        """
        textCtrl = self.GetWindow()
        text = textCtrl.GetValue()

        if len(text) == 0:
            wx.MessageBox("A text object must contain some text!", "Error")
            textCtrl.SetBackgroundColour("pink")
            textCtrl.SetFocus()
            textCtrl.Refresh()
            return False
        else:
            textCtrl.SetBackgroundColour(
                wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
            textCtrl.Refresh()
            return True

    def TransferToWindow(self):
        """ Transfer data from validator to window.

            The default implementation returns False, indicating that an error
            occurred.  We simply return True, as we don't do any data transfer.
        """
        return True  # Prevent wxDialog from complaining.

    def TransferFromWindow(self):
        """ Transfer data from window to validator.

            The default implementation returns False, indicating that an error
            occurred.  We simply return True, as we don't do any data transfer.
        """
        return True  # Prevent wxDialog from complaining.


if __name__ == "__main__":
    app = wx.App(False)
    frame = MainWindows(None)
    frame.Show(True)
    app.MainLoop()
