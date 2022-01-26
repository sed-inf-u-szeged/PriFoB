package hu.sed.prifob

import android.os.Bundle
import android.util.Log
import androidx.fragment.app.Fragment
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.*
import androidx.core.view.children
import androidx.navigation.fragment.findNavController
import com.android.volley.Request
import com.android.volley.Response
import com.android.volley.toolbox.JsonObjectRequest
import hu.sed.prifob.dummy.Profession
import org.json.JSONArray
import org.json.JSONObject
import java.util.ArrayList

// TODO: Rename parameter arguments, choose names that match
// the fragment initialization parameters, e.g. ARG_ITEM_NUMBER
private const val ARG_PARAM1 = "param1"
private const val ARG_PARAM2 = "param2"

val attributesData = "[First_name, Last_name, STD_ID, SSN, etc]"

/**
 * A simple [Fragment] subclass.
 * Use the [SchemaFragment.newInstance] factory method to
 * create an instance of this fragment.
 */
class SchemaFragment : Fragment() {
    // TODO: Rename and change types of parameters
    private var param1: String? = null
    private var param2: String? = null

    var ITEMS: JSONArray? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        arguments?.let {
            param1 = it.getString(ARG_PARAM1)
            param2 = it.getString(ARG_PARAM2)
        }

        if(requireActivity() is MainActivity){
            val mainActivity : MainActivity = requireActivity() as MainActivity
            if(mainActivity.currAttributes != null){
                ITEMS = JSONArray(mainActivity.currAttributes)
            }else{
                Toast.makeText(
                        context, "ERROR parsing attributes", Toast.LENGTH_SHORT
                ).show()
            }
        }

    }

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        // Inflate the layout for this fragment

        val view: View = inflater.inflate(R.layout.fragment_schema, container, false)

        val attributesLL = view.findViewById<LinearLayout>(R.id.attributes_ll)

        attributesLL.removeAllViewsInLayout()

        val jsonArray = ITEMS
        if (jsonArray != null) {
            for (i in 0 until jsonArray.length()) {
                Log.d("SchemaFragment","for: " + jsonArray.get(i))
                val textView: TextView = TextView(context)

                // Creating a LinearLayout.LayoutParams object for text view
                var paramsTv : ViewGroup.LayoutParams = ViewGroup.LayoutParams(
                        ViewGroup.LayoutParams.MATCH_PARENT, // This will define text view width
                        ViewGroup.LayoutParams.WRAP_CONTENT // This will define text view height
                )
                textView.layoutParams = paramsTv
                textView.text = jsonArray.getString(i)

                val editText: TextView = EditText(context)

                // Creating a LinearLayout.LayoutParams object for text view
                var paramsEt : ViewGroup.LayoutParams = ViewGroup.LayoutParams(
                        ViewGroup.LayoutParams.MATCH_PARENT, // This will define text view width
                        ViewGroup.LayoutParams.WRAP_CONTENT // This will define text view height
                )
                editText.layoutParams = paramsEt

                attributesLL.addView(textView)
                attributesLL.addView(editText)
            }
        }

        view.findViewById<Button>(R.id.btn_submit).setOnClickListener({
            view ->
            //TODO validate?
            var credentialJson: JSONObject = JSONObject()
            //var attributes : HashMap<String, String> = HashMap()
            var attributesJson: JSONObject = JSONObject()
            for (i in 0 until attributesLL.children.count()/2) {
                Log.d("SchemaFragment", "attributesLLi " + i)
                var key = (attributesLL.getChildAt(i*2) as TextView).text.trim().toString()
                Log.d("SchemaFragment", "key " + key)
                var value = (attributesLL.getChildAt(i*2+1) as EditText).text.trim().toString()
                Log.d("SchemaFragment", "value " + value)
                attributesJson.put(key, value)
            }

            credentialJson.put(Constants.DID_IDENTIFIER, (requireActivity() as MainActivity).currDID)
            credentialJson.put(Constants.SCHEMA_IDENTIFIER, (requireActivity() as MainActivity).currSchema)
            credentialJson.put(Constants.ATTRIBUTES, attributesJson)

            var contentJson: JSONObject = JSONObject()
            contentJson.put(Constants.CREDENTIAL, credentialJson)

            Log.d("SchemaFragment", "contentJson: " + contentJson.toString())

            val url = "http://10.0.2.2:5000/prifobapi/v1.0/credential"
            val jsonObjectRequest = JsonObjectRequest(Request.Method.POST, url, contentJson,
                    Response.Listener { response ->
                        Log.d("SchemaFragment",response.toString())

                        Toast.makeText(
                                context, "Request submitted",
                                Toast.LENGTH_SHORT
                        ).show()

                        if(requireActivity() is MainActivity){
                            val mainActivity : MainActivity = requireActivity() as MainActivity
                            //TODO Exceptions....
                            var repo:CredentialRepository = mainActivity.getCredentialRepositoryInstance(requireContext())

                            var respJson: JSONObject = JSONObject(response.toString())
                            var filename: String = ""
                            filename += respJson.getJSONObject(Constants.CREDENTIAL).getString(Constants.DID_IDENTIFIER)
                            filename += respJson.getJSONObject(Constants.CREDENTIAL).getString(Constants.SCHEMA_IDENTIFIER)
                            repo.saveContent(response.toString(), filename)

                            findNavController().navigate(R.id.action_SchemaFragment_to_CredentialsFragment)

                        }

                    },
                    Response.ErrorListener { error ->
                        // TODO: Handle error
                        Log.e("SchemaFragment",error.toString())

                        Toast.makeText(
                                context, "ERROR " + error.localizedMessage,
                                Toast.LENGTH_SHORT
                        ).show()
                    }
            )

            // Access the RequestQueue through your singleton class.
            RQSingleton.getInstance(requireContext()).addToRequestQueue(jsonObjectRequest)
        })

        return view
    }

    companion object {
        /**
         * Use this factory method to create a new instance of
         * this fragment using the provided parameters.
         *
         * @param param1 Parameter 1.
         * @param param2 Parameter 2.
         * @return A new instance of fragment SchemaFragment.
         */
        // TODO: Rename and change types and number of parameters
        @JvmStatic
        fun newInstance(param1: String, param2: String) =
            SchemaFragment().apply {
                arguments = Bundle().apply {
                    putString(ARG_PARAM1, param1)
                    putString(ARG_PARAM2, param2)
                }
            }
    }
}