package hu.sed.prifob

import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.view.MenuItem
import androidx.activity.result.ActivityResultLauncher
import androidx.appcompat.app.AppCompatActivity
import androidx.appcompat.widget.Toolbar
import androidx.navigation.NavController
import androidx.navigation.Navigation
import androidx.navigation.findNavController
import androidx.navigation.fragment.NavHostFragment
import androidx.navigation.ui.*
import org.json.JSONObject
import java.security.cert.Certificate


class MainActivity : AppCompatActivity() {

    private lateinit var appBarConfiguration: AppBarConfiguration
    private lateinit var mQrResultLauncher : ActivityResultLauncher<Intent>

    lateinit var institutionsJson : JSONObject
    lateinit var currDID : String
    lateinit var currSchemas : String
    lateinit var currSchema : String
    lateinit var currAttributes : String

    lateinit var selectedCred : Credential

    var institutionsJsonArray = null

    @Volatile private var INSTANCE: CredentialRepository? = null

    fun getCredentialRepositoryInstance(context: Context): CredentialRepository =
            INSTANCE ?: synchronized(this) {
                INSTANCE ?: CredentialRepository(context).also { INSTANCE = it }
            }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        val navController :NavController = Navigation.findNavController(this, R.id.nav_host_fragment)

        NavigationUI.setupWithNavController(findViewById(R.id.toolbar) as Toolbar, navController)

        //setSupportActionBar(findViewById(R.id.toolbar))

        /*
        mQrResultLauncher = registerForActivityResult(ActivityResultContracts.StartActivityForResult()) {
            if(it.resultCode == Activity.RESULT_OK) {
                val result = IntentIntegrator.parseActivityResult(it.resultCode, it.data)

                if(result.contents != null) {
                    // Do something with the contents (this is usually a URL)
                    println(result.contents)
                }
            }
        }
        */
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        return when (item.itemId) {
            R.id.action_settings -> true
            else -> super.onOptionsItemSelected(item)
        }
    }

    override fun onSupportNavigateUp(): Boolean {
        val navController = findNavController(R.id.nav_host_fragment)
        return navController.navigateUp(appBarConfiguration) || super.onSupportNavigateUp()
    }
}