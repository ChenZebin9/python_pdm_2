using EdmLib;
using System;

namespace EpdmTest
{
    public class EpdmTest
    {
        [System.Runtime.InteropServices.DllImport("user32.dll")]
        public static extern int GetForegroundWindow();

        private EdmVault5 _v5 = null;
        private IEdmVault16 _v16 = null;
        private IEdmUser10 _user = null;

        public EpdmTest()
        {
            _v5 = new EdmVault5();
            _v16 = (IEdmVault16)_v5;
        }

        public bool Login()
        {
            _v16.LoginAuto("Greatoo_JJ", GetForegroundWindow());
            return _v16.IsLoggedIn;
        }

        public string GetUserName()
        {
            if (_v16 != null && _v16.IsLoggedIn)
            {
                var userMgr = (IEdmUserMgr8)_v5;
                _user = (IEdmUser10)userMgr.GetLoggedInUser();
                return _user.FullName;
            }
            return string.Empty;
        }

        static void main(string[] args)
        {
            var aTest = new EpdmTest();
            if(aTest.Login()){
                var userName = aTest.GetUserName();
                Console.WriteLine(string.format("Is logged in. Username is {0}.", Username));
                Console.ReadKey();
            }
        }
    }
}