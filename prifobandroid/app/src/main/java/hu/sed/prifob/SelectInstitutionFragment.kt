package hu.sed.prifob

import android.os.Bundle
import android.util.Log
import androidx.fragment.app.Fragment
import androidx.recyclerview.widget.GridLayoutManager
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.navigation.fragment.findNavController
import com.android.volley.Request
import com.android.volley.Response
import com.android.volley.toolbox.JsonObjectRequest
import hu.sed.prifob.dummy.DummyContent
import hu.sed.prifob.dummy.Institution
import org.json.JSONArray
import org.json.JSONObject
import java.util.ArrayList

/**
 * A fragment representing a list of Items.
 */
class SelectInstitutionFragment : Fragment() {

    private var columnCount = 1
    val ITEMS: MutableList<Institution.InstitutionItem> = ArrayList()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        arguments?.let {
            columnCount = it.getInt(ARG_COLUMN_COUNT)
        }


        if(requireActivity() is MainActivity){
            val mainActivity : MainActivity = requireActivity() as MainActivity
            if(mainActivity.institutionsJson.has("institutions")){
                val institutionsArray : JSONArray = mainActivity.institutionsJson.getJSONArray("institutions")
                ITEMS.clear()
                for (i in 0 until institutionsArray.length()) {
                    val item : JSONObject= institutionsArray.getJSONObject(i)
                    if( item.has(Constants.DID_IDENTIFIER) ){
                        val name = item.getString(Constants.DID_IDENTIFIER)

                        if(item.has(Constants.SCHEMAS)){
                            val schemas = item.getJSONArray(Constants.SCHEMAS).toString()
                            ITEMS.add(Institution.InstitutionItem(i.toString(), name, schemas))
                        }else{
                            Toast.makeText(
                                    context, "ERROR parsing SCHEMAS", Toast.LENGTH_SHORT
                            ).show()
                        }
                    }else{
                        Toast.makeText(
                                context, "ERROR parsing DID", Toast.LENGTH_SHORT
                        ).show()
                    }

                }
            }else{
                Toast.makeText(
                        context, "ERROR parsing institutions", Toast.LENGTH_SHORT
                ).show()
            }

        }
    }

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        val view = inflater.inflate(R.layout.fragment_select_institution_list, container, false)

        // Set the adapter
        if (view is RecyclerView) {
            with(view) {
                layoutManager = when {
                    columnCount <= 1 -> LinearLayoutManager(context)
                    else -> GridLayoutManager(context, columnCount)
                }
                adapter = SelectInstitutionAdapter(ITEMS)
            }
        }

        return view
    }

    companion object {

        // TODO: Customize parameter argument names
        const val ARG_COLUMN_COUNT = "column-count"

        // TODO: Customize parameter initialization
        @JvmStatic
        fun newInstance(columnCount: Int) =
            SelectInstitutionFragment().apply {
                arguments = Bundle().apply {
                    putInt(ARG_COLUMN_COUNT, columnCount)
                }
            }
    }
}