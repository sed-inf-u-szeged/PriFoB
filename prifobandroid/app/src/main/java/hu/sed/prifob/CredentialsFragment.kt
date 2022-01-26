package hu.sed.prifob

import android.content.Context
import android.os.Bundle
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.ListView
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.navigation.fragment.findNavController
import com.android.volley.Request
import com.android.volley.Response
import com.android.volley.toolbox.JsonObjectRequest
import com.google.android.material.floatingactionbutton.FloatingActionButton
import org.json.JSONObject


// TODO: Rename parameter arguments, choose names that match
// the fragment initialization parameters, e.g. ARG_ITEM_NUMBER
private const val ARG_PARAM1 = "param1"
private const val ARG_PARAM2 = "param2"

/**
 * A simple [Fragment] subclass.
 * Use the [CredentialsFragment.newInstance] factory method to
 * create an instance of this fragment.
 */
class CredentialsFragment : Fragment() {
    // TODO: Rename and change types of parameters
    private var param1: String? = null
    private var param2: String? = null

    var isRequestMenuShown: Boolean = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        arguments?.let {
            param1 = it.getString(ARG_PARAM1)
            param2 = it.getString(ARG_PARAM2)
        }
    }

    override fun onCreateView(
            inflater: LayoutInflater, container: ViewGroup?,
            savedInstanceState: Bundle?
    ): View? {
        // Inflate the layout for this fragment
        val view: View = inflater.inflate(R.layout.fragment_credentials, container, false)

        var creds = (requireActivity() as MainActivity).getCredentialRepositoryInstance(requireContext()).getCredentials()
        Log.d("CredentialsFragment", "creds: " + creds.toString())

        for(cred in creds){
            Log.d("CredentialsFragment", "cred: " + cred.institution + " " + cred.profession)
        }

        view.findViewById<Button>(R.id.btn_profile).setOnClickListener{
            Toast.makeText(
                    context, "Profile",
                    Toast.LENGTH_SHORT
            ).show()
            findNavController().navigate(R.id.action_CredentialsFragment_to_ProfileFragment)
        }

        view.findViewById<Button>(R.id.btn_notifications).setOnClickListener{
            Toast.makeText(
                    context, "Notifications",
                    Toast.LENGTH_SHORT
            ).show()
        }

        view.findViewById<FloatingActionButton>(R.id.fbtn_add).setOnClickListener{
            requestMenu()
            Toast.makeText(
                    context, "Request credential menu",
                    Toast.LENGTH_SHORT
            ).show()
        }

        view.findViewById<FloatingActionButton>(R.id.fbtn_add_institution).setOnClickListener{
            Toast.makeText(
                    context, "Request credential from institution",
                    Toast.LENGTH_SHORT
            ).show()

            val url = "http://10.0.2.2:5000/prifobapi/v1.0/institutions"
            Log.d("UserFragment","jsonArrayRequest")
            val jsonObjectRequest = JsonObjectRequest(Request.Method.GET, url, null,
                    Response.Listener { response ->
                        Log.d("UserFragment",response.toString())

                        Toast.makeText(
                                context, "Institution list downloaded",
                                Toast.LENGTH_SHORT
                        ).show()

                        if(requireActivity() is MainActivity){
                            val mainActivity : MainActivity = requireActivity() as MainActivity

                            //TODO Exceptions....
                            mainActivity.institutionsJson = JSONObject(response.toString())

                            findNavController().navigate(R.id.action_CredentialsFragment_to_SelectInstitutionFragment)

                        }

                    },
                    Response.ErrorListener { error ->
                        // TODO: Handle error
                        Log.e("UserFragment",error.toString())

                        Toast.makeText(
                                context, "ERROR " + error.localizedMessage,
                                Toast.LENGTH_SHORT
                        ).show()
                    }
            )

            // Access the RequestQueue through your singleton class.
            RQSingleton.getInstance(requireContext()).addToRequestQueue(jsonObjectRequest)



        }

        view.findViewById<FloatingActionButton>(R.id.fbtn_add_other).setOnClickListener{
            Toast.makeText(
                    context, "Request credential from user",
                    Toast.LENGTH_SHORT
            ).show()
            //findNavController().navigate(R.id.action_UserFragment_to_CredentialFragment)

            /*
            val scanner = IntentIntegrator(this)
            // QR Code Format
            scanner.setDesiredBarcodeFormats(IntentIntegrator.QR_CODE)
            // Set Text Prompt at Bottom of QR code Scanner Activity
            scanner.setPrompt("QR Code Scanner Prompt Text")
            // Start Scanner (don't use initiateScan() unless if you want to use OnActivityResult)
            mQrResultLauncher.launch(scanner.createScanIntent())
            */
        }



        return view
    }

    fun getCredentials(): ArrayList<Credential> {
        val credentials = ArrayList<Credential>()

        var credsFromFiles: ArrayList<Credential> = (requireActivity() as MainActivity).getCredentialRepositoryInstance(requireContext()).getCredentials()
        if(credsFromFiles.isEmpty()) {
            credentials.add(Credential("My IT Certification", "University of Szeged", "Computer Science BSc", HashMap()))
            credentials.add(Credential("Art degree", "Yale University", "Graphic Design", HashMap()))
        }else{
            credentials.addAll(credsFromFiles)
        }
        /*
       credentials.add(Credential("Empleyee A's cert", "Florida State University", "Music Teacher"))
       credentials.add(Credential("Empleyee B's cert", "School of the Art Institute of Chicago", "Fine and Studio Arts Management"))
       credentials.add(Credential("Empleyee C's cert", "California Institute of the Arts", "Drama and Dance Teacher Education"))
       credentials.add(Credential("Empleyee D's cert", "Rhode Island School of Design", "Digital Arts"))
        */

        /*
        var certificationsDir = context?.getDir("certifications", Context.MODE_PRIVATE)
        var certificationFilesList = certificationsDir?.listFiles()
        if (certificationFilesList != null) {
            for(certificationFile in certificationFilesList) {
                Log.d("UserFragment", "certificationFilesList: " + certificationFile)
                //context.openFileInput(certificationFile.)
                val certificationString = certificationFile.bufferedReader().use { it.readText() }
                //JSONObject certificationJson = new JSONObject(certificationString)
                Log.d("UserFragment", "certificationString: " + certificationString)
                val certificationJson = JSONObject(certificationString)
                val cred: JSONObject = certificationJson.getJSONObject(Constants.CREDENTIAL)
                var institution = ""
                var profession = ""
                val attributes = HashMap<String,String>()
                for(key in cred.keys()){
                    if(key.equals(Constants.DID_IDENTIFIER)){
                        institution = cred.getString(key)
                    }else if(key.equals(Constants.SCHEMA_IDENTIFIER)){
                        profession = cred.getString(key)
                    }else{
                        attributes.put(key, cred.getString(key))
                    }
                }
                credentials.add(Credential(certificationFile.name, institution, profession, attributes))
            }
        }
        */
        return credentials
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {

        val credentials_lv = view.findViewById<ListView>(R.id.list_credentials) as ListView

        val credentials = getCredentials()

        val credentialsAdapter = CredentialAdapter(credentials, requireContext())
        credentials_lv.adapter = credentialsAdapter

        view.findViewById<ListView>(R.id.list_credentials).setOnItemClickListener { parent, view, position, id ->
            val element = credentialsAdapter.getItem(position) // The item that was clicked

                Toast.makeText(
                        context, "Credential " + element?.name,
                        Toast.LENGTH_SHORT
                ).show()

                (requireActivity() as MainActivity).selectedCred = element!!

                findNavController().navigate(R.id.action_CredentialsFragment_to_CredentialFragment)
        }


    }

    fun requestMenu(){
        if(isRequestMenuShown){

        }else{

        }
    }

    companion object {
        /**
         * Use this factory method to create a new instance of
         * this fragment using the provided parameters.
         *
         * @param param1 Parameter 1.
         * @param param2 Parameter 2.
         * @return A new instance of fragment UserFragment.
         */
        // TODO: Rename and change types and number of parameters
        @JvmStatic
        fun newInstance(param1: String, param2: String) =
            CredentialsFragment().apply {
                arguments = Bundle().apply {
                    putString(ARG_PARAM1, param1)
                    putString(ARG_PARAM2, param2)
                }
            }
    }
}
/*
@Composable
fun MessageCard(name: String) {
    Text(text = "Hello $name!")
}

@Preview
@Composable
fun PreviewMessageCard() {
    MessageCard(
            msg = Message("Colleague", "Hey, take a look at Jetpack Compose, it's great!")
    )
}

 */