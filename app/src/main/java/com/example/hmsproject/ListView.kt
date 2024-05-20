package com.example.hmsproject

import android.app.Activity
import android.content.Intent
import android.os.Bundle
import android.view.View
import android.view.ViewGroup
import android.widget.BaseAdapter
import android.widget.ImageView
import android.widget.ListView
import android.widget.TextView
import android.widget.Toast

class ListView : Activity() { //该listview是用于选择被监护人的那个界面
    private val titles = arrayOf("爸爸", "妈妈")
    private val prices = arrayOf("就诊：浙江省中医院", "暂无就医信息")
    private val ages = arrayOf("年龄：75", "年龄：73")
    private val icons = intArrayOf(R.drawable.oldman2, R.drawable.oldwoman)

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_list_view)

        val mListView: ListView = findViewById(R.id.lv)

        val mAdapter = MyBaseAdapter()

        mListView.adapter = mAdapter
    }

    inner class MyBaseAdapter : BaseAdapter() {
        override fun getCount(): Int {
            return titles.size
        }

        override fun getItem(position: Int): Any {
            return titles[position]
        }

        override fun getItemId(position: Int): Long {
            return position.toLong()
        }

        override fun getView(position: Int, convertView: View?, parent: ViewGroup?): View {
            var convertView = convertView
            val holder: ViewHolder
            if (convertView == null) {
                convertView = View.inflate(this@ListView, R.layout.list_view_header, null)
                holder = ViewHolder()
                holder.title = convertView.findViewById(R.id.title)
                holder.age = convertView.findViewById(R.id.age)
                holder.price = convertView.findViewById(R.id.price)
                holder.iv = convertView.findViewById(R.id.iv)
                convertView.tag = holder
            } else {
                holder = convertView.tag as ViewHolder
            }

            // 设置点击事件
            convertView?.setOnClickListener {
                // 根据位置区分点击事件
                when (position) {
                    0 -> {
                        // 第一个项的点击事件
                        val intent = Intent(this@ListView, MainPageActivity::class.java)
                        startActivity(intent)
                    }
                    1 -> {
                        // 第二个项的点击事件
                        // 在这里显示相应的提示信息
                        showToast("抱歉，家属目前并未就医")
                    }
                    // 添加更多的项的点击事件，如果需要的话
                }
            }

            holder.title.text = titles[position]
            holder.age.text = ages[position]
            holder.price.text = prices[position]
            holder.iv.setBackgroundResource(icons[position])
            return convertView!!
        }
    }

    internal class ViewHolder {
        lateinit var title: TextView
        lateinit var age: TextView
        lateinit var price: TextView
        lateinit var iv: ImageView
    }

    private fun showToast(message: String) {
        // 在这里实现显示提示信息的逻辑，可以使用 Toast 或其他方式
        // 示例中直接使用 Toast，你可以根据需要进行修改
        Toast.makeText(this, message, Toast.LENGTH_SHORT).show()
    }
}
