package hu.sed.prifob

import android.os.Bundle
import androidx.fragment.app.Fragment
import androidx.recyclerview.widget.GridLayoutManager
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import hu.sed.prifob.dummy.DummyContent
import hu.sed.prifob.dummy.Institution
import hu.sed.prifob.dummy.Profession
import org.json.JSONArray
import org.json.JSONObject
import java.util.ArrayList

/**
 * A fragment representing a list of Items.
 */
class SelectProfessionFragment : Fragment() {

    private var columnCount = 1
    val ITEMS: MutableList<Profession.ProfessionItem> = ArrayList()


    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        arguments?.let {
            columnCount = it.getInt(ARG_COLUMN_COUNT)
        }

        if(requireActivity() is MainActivity){
            val mainActivity : MainActivity = requireActivity() as MainActivity
            if(mainActivity.currSchemas != null){
                val schemas :JSONArray = JSONArray(mainActivity.currSchemas)
                ITEMS.clear()
                for (i in 0 until schemas.length()) {
                    val item: JSONObject = schemas.getJSONObject(i)
                    if (item.has(Constants.SCHEMA_IDENTIFIER)) {
                        val name = item.getString(Constants.SCHEMA_IDENTIFIER)

                        if (item.has(Constants.ATTRIBUTES)) {
                            val attributes = item.getJSONArray(Constants.ATTRIBUTES).toString()
                            ITEMS.add(Profession.ProfessionItem(i.toString(), name, attributes))
                        } else {
                            Toast.makeText(
                                    context, "ERROR parsing ATTRIBUTES", Toast.LENGTH_SHORT
                            ).show()
                        }
                    } else {
                        Toast.makeText(
                                context, "ERROR parsing SCHEMA_IDENTIFIER", Toast.LENGTH_SHORT
                        ).show()
                    }
                }

            }else{
                Toast.makeText(
                        context, "ERROR parsing schemas", Toast.LENGTH_SHORT
                ).show()
            }
        }
    }

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?,
                              savedInstanceState: Bundle?): View? {
        val view = inflater.inflate(R.layout.fragment_select_profession_list, container, false)

        // Set the adapter
        if (view is RecyclerView) {
            with(view) {
                layoutManager = when {
                    columnCount <= 1 -> LinearLayoutManager(context)
                    else -> GridLayoutManager(context, columnCount)
                }
                adapter = SelectProfessionAdapter(ITEMS)
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
                SelectProfessionFragment().apply {
                    arguments = Bundle().apply {
                        putInt(ARG_COLUMN_COUNT, columnCount)
                    }
                }
    }
}