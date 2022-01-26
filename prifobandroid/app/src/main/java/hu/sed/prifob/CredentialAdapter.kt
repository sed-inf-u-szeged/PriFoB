package hu.sed.prifob

import android.content.Context
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.*
import java.util.*

class CredentialAdapter(items: ArrayList<Credential>, ctx: Context) :
    ArrayAdapter<Credential>(ctx, R.layout.list_item_credential, items) {

    //view holder is used to prevent findViewById calls
    private class AttractionItemViewHolder {
        internal var name: TextView? = null
        internal var institution: TextView? = null
        internal var profession: TextView? = null
        internal var rename: ImageButton? = null
        internal var validate: ImageButton? = null
        internal var delete: ImageButton? = null
    }

    var hideButtons: Boolean = false

    override fun getView(i: Int, view: View?, viewGroup: ViewGroup): View {
        var view = view

        val viewHolder: AttractionItemViewHolder

        if (view == null) {
            val inflater = LayoutInflater.from(context)
            view = inflater.inflate(R.layout.list_item_credential, viewGroup, false)

            viewHolder = AttractionItemViewHolder()
            viewHolder.name = view!!.findViewById<View>(R.id.name) as TextView
            viewHolder.institution = view.findViewById<View>(R.id.institution) as TextView
            viewHolder.profession = view.findViewById<View>(R.id.profession) as TextView
            //viewHolder.rename = view.findViewById<View>(R.id.btn_rename) as ImageButton
            //viewHolder.validate = view.findViewById<View>(R.id.btn_validate) as ImageButton
            //viewHolder.delete = view.findViewById<View>(R.id.btn_delete) as ImageButton

        } else {
            //no need to call findViewById, can use existing ones from saved view holder
            viewHolder = view.tag as AttractionItemViewHolder
        }

        val credential = getItem(i)
        viewHolder.name!!.text = credential!!.name
        viewHolder.institution!!.text = credential.institution
        viewHolder.profession!!.text = credential.profession

        /*
        if(hideButtons){
            viewHolder.rename!!.visibility = View.INVISIBLE
            viewHolder.validate!!.visibility = View.INVISIBLE
            viewHolder.delete!!.visibility = View.INVISIBLE
        }else {
            viewHolder.rename!!.visibility = View.VISIBLE
            viewHolder.validate!!.visibility = View.VISIBLE
            viewHolder.delete!!.visibility = View.VISIBLE
            //handle events of views of items
            viewHolder.rename!!.setOnClickListener {
                Toast.makeText(
                    context, "Rename " + credential!!.name,
                    Toast.LENGTH_SHORT
                ).show()
            }

            viewHolder.validate!!.setOnClickListener {
                Toast.makeText(
                    context, "Validate " + credential!!.name,
                    Toast.LENGTH_SHORT
                ).show()
            }

            viewHolder.delete!!.setOnClickListener {
                Toast.makeText(
                    context, "Delete " + credential!!.name,
                    Toast.LENGTH_SHORT
                ).show()
            }
        }
        */

        view.tag = viewHolder

        return view
    }
}