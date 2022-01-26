package hu.sed.prifob

import android.os.Bundle
import androidx.fragment.app.Fragment
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.TextView
import androidx.core.view.marginLeft

// TODO: Rename parameter arguments, choose names that match
// the fragment initialization parameters, e.g. ARG_ITEM_NUMBER
private const val ARG_PARAM1 = "param1"
private const val ARG_PARAM2 = "param2"

/**
 * A simple [Fragment] subclass.
 * Use the [CredentialFragment.newInstance] factory method to
 * create an instance of this fragment.
 */
class CredentialFragment : Fragment() {
    // TODO: Rename and change types of parameters
    private var param1: String? = null
    private var param2: String? = null

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
        var view = inflater.inflate(R.layout.fragment_credential, container, false)
        var cred = (requireActivity() as MainActivity).selectedCred

        view.findViewById<TextView>(R.id.profession).text = cred.profession
        view.findViewById<TextView>(R.id.institution).text = cred.institution

        for(key in cred.attributes.keys){
            val textViewKey: TextView = TextView(context)

            // Creating a LinearLayout.LayoutParams object for text view
            var paramsTv : ViewGroup.LayoutParams = ViewGroup.LayoutParams(
                    ViewGroup.LayoutParams.MATCH_PARENT, // This will define text view width
                    ViewGroup.LayoutParams.WRAP_CONTENT // This will define text view height
            )

            textViewKey.layoutParams = paramsTv
            textViewKey.text = key.toString() + ": " + cred.attributes.get(key).toString()

            view.findViewById<LinearLayout>(R.id.attributes_ll).addView(textViewKey)

        }


        return view
    }

    companion object {
        /**
         * Use this factory method to create a new instance of
         * this fragment using the provided parameters.
         *
         * @param param1 Parameter 1.
         * @param param2 Parameter 2.
         * @return A new instance of fragment CredentialFragment.
         */
        // TODO: Rename and change types and number of parameters
        @JvmStatic
        fun newInstance(param1: String, param2: String) =
            CredentialFragment().apply {
                arguments = Bundle().apply {
                    putString(ARG_PARAM1, param1)
                    putString(ARG_PARAM2, param2)
                }
            }
    }
}