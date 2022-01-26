package hu.sed.prifob

import androidx.recyclerview.widget.RecyclerView
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import android.widget.Toast
import androidx.navigation.findNavController

import hu.sed.prifob.dummy.DummyContent.DummyItem
import hu.sed.prifob.dummy.Profession

/**
 * [RecyclerView.Adapter] that can display a [DummyItem].
 * TODO: Replace the implementation with code for your data type.
 */
class SelectProfessionAdapter(
        private val values: List<Profession.ProfessionItem>)
    : RecyclerView.Adapter<SelectProfessionAdapter.ViewHolder>() {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
                .inflate(R.layout.fragment_select_profession, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val item = values[position]
        holder.idView.text = item.id
        holder.contentView.text = item.content

        holder.itemView.setOnClickListener{ view ->
            val mainActivity = view.context as MainActivity
            mainActivity.currSchema = item.content
            mainActivity.currAttributes = item.details
            view.findNavController().navigate(R.id.action_SelectProfessionFragment_to_SchemaFragment)
            Toast.makeText(
                view.context, "Profession selected",
                Toast.LENGTH_SHORT
            ).show()
        }
    }

    override fun getItemCount(): Int = values.size

    inner class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val idView: TextView = view.findViewById(R.id.item_number)
        val contentView: TextView = view.findViewById(R.id.content)

        override fun toString(): String {
            return super.toString() + " '" + contentView.text + "'"
        }
    }
}