import silegon
import unittest

class SilegonTestCase(unittest.TestCase):

    def setUp(self):
        silegon.app.config['DATABASE_DB'] += '_test'
        silegon.app.config['TESTING'] = True
        self.app = silegon.app.test_client()
        db_link = silegon.connect_db().cursor()
        db_link.execute("create database %s;"%(silegon.app.config['DATABASE_DB']))
        db_link.execute("use %s;"%(silegon.app.config['DATABASE_DB']))
        silegon.init_db()
        db_link.close()

    def tearDown(self):
        db_link = silegon.connect_db().cursor()
        db_link.execute("drop database %s;"%(silegon.app.config['DATABASE_DB']))
        db_link.close()
        print silegon.app.config['DATABASE_DB']

    def test_empty_db(self):
        pass

if __name__=='__main__':
    unittest.main()
