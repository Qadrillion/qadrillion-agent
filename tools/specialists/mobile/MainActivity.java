package com.qadrillion.parcel;

import android.app.Activity;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.text.InputType;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.TextView;

public class MainActivity extends Activity {
    private SharedPreferences ledger;
    private int parcels;
    private int units;
    private TextView parcelCount;
    private TextView unitCount;
    private TextView validation;
    private EditText quantity;

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        ledger = getSharedPreferences("ledger", MODE_PRIVATE);
        parcels = ledger.getInt("parcels", 0);
        units = ledger.getInt("units", 0);
        LinearLayout layout = new LinearLayout(this);
        layout.setOrientation(LinearLayout.VERTICAL);
        int padding = (int) (24 * getResources().getDisplayMetrics().density);
        layout.setPadding(padding, padding, padding, padding);
        TextView title = new TextView(this);
        title.setText("Parcel ledger");
        title.setTextSize(26);
        layout.addView(title);
        TextView label = new TextView(this);
        label.setText("Units per parcel (1 to 5)");
        label.setTextSize(18);
        label.setLabelFor(R.id.quantity);
        layout.addView(label);
        quantity = new EditText(this);
        quantity.setId(R.id.quantity);
        quantity.setContentDescription("Units per parcel");
        quantity.setInputType(InputType.TYPE_CLASS_NUMBER | InputType.TYPE_NUMBER_FLAG_SIGNED);
        layout.addView(quantity);
        Button add = new Button(this);
        add.setId(R.id.add_parcel);
        add.setText("Add parcel");
        add.setOnClickListener(view -> addParcel());
        layout.addView(add);
        validation = new TextView(this);
        validation.setId(R.id.validation);
        validation.setAccessibilityLiveRegion(TextView.ACCESSIBILITY_LIVE_REGION_POLITE);
        layout.addView(validation);
        parcelCount = new TextView(this);
        parcelCount.setId(R.id.parcel_count);
        parcelCount.setTextSize(20);
        layout.addView(parcelCount);
        unitCount = new TextView(this);
        unitCount.setId(R.id.unit_count);
        unitCount.setTextSize(20);
        layout.addView(unitCount);
        setContentView(layout);
        renderCounts();
    }

    private void addParcel() {
        int value;
        try {
            value = Integer.parseInt(quantity.getText().toString());
        } catch (NumberFormatException error) {
            value = 0;
        }
        if (value < 1 || value > 5) {
            validation.setText("Enter a whole number from 1 to 5");
            return;
        }
        parcels++;
        units += value;
        SharedPreferences.Editor edit = ledger.edit().putInt("parcels", parcels);
        if (BuildConfig.SAVE_TOTAL) {
            edit.putInt("units", units);
        }
        edit.commit();
        validation.setText("Parcel added");
        quantity.setText("");
        renderCounts();
    }

    private void renderCounts() {
        parcelCount.setText("Parcels: " + parcels);
        unitCount.setText("Units: " + units);
    }
}
