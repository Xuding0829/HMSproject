package com.example.hmsproject


import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.viewpager2.widget.ViewPager2
import com.example.hmsproject.Adapter.ViewPagerAdapter
import com.google.android.material.tabs.TabLayout
import com.google.android.material.tabs.TabLayoutMediator


class MainPageActivity : AppCompatActivity() {
    private lateinit var viewPager: ViewPager2
    private lateinit var tabLayout: TabLayout
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        this.viewPager = findViewById(R.id.viewPager)
        this.tabLayout = findViewById(R.id.tabLayout)

        viewPager.adapter = ViewPagerAdapter(this)


        TabLayoutMediator(tabLayout, viewPager) { tab, position ->
            tab.text = when(position) {
                0 -> "就诊情况"
                1 -> "在院位置"
                2 -> "诊断结果"
                else -> "医疗商城"
            }
        }.attach()
    }
}


