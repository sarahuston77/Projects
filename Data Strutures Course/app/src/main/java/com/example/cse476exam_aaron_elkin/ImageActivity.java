package com.example.cse476exam_aaron_elkin;

import android.content.Context;
import android.content.Intent;
import android.graphics.drawable.Drawable;
import android.net.ConnectivityManager;
import android.net.NetworkCapabilities;
import android.os.Bundle;
import android.text.TextUtils;
import android.view.View;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.Toast;

import androidx.activity.EdgeToEdge;
import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

import com.bumptech.glide.Glide;
import com.bumptech.glide.load.DataSource;
import com.bumptech.glide.load.engine.DiskCacheStrategy;
import com.bumptech.glide.load.engine.GlideException;
import com.bumptech.glide.request.RequestListener;
import com.bumptech.glide.request.target.Target;

public class ImageActivity extends AppCompatActivity {
    private EditText mUrlEditText;
    private ImageView mPlaceholderImage;
    private String mSavedUrl = null;
    private Boolean mUrlSaved = false;

    // Request listener for glide, checks if the image could load (mainly if the url was valid)
    // and displays appropiate messages and sets variables
    private RequestListener<Drawable> requestListener = new RequestListener<Drawable>() {
        @Override
        public boolean onLoadFailed(@Nullable GlideException e, Object model, Target<Drawable> target, boolean isFirstResource) {
            mUrlSaved = false;
            Toast.makeText(ImageActivity.this, "Image load failed.", Toast.LENGTH_SHORT).show();
            return false;
        }

        @Override
        public boolean onResourceReady(@Nullable Drawable resource, Object model, Target<Drawable> target, DataSource dataSource, boolean isFirstResource) {
            mUrlSaved = true;
            mSavedUrl = model.toString(); // Save the URL when the image loads successfully
            Toast.makeText(ImageActivity.this, "Image loaded successfully.", Toast.LENGTH_SHORT).show();
            return false;
        }
    };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_image);
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
            return insets;
        });

        mUrlEditText = findViewById(R.id.urlInput);
        mPlaceholderImage = findViewById(R.id.placeholderImage);

        if (savedInstanceState != null)
        {
            // If there was previously a saved url, then
            mUrlSaved = savedInstanceState.getBoolean("urlSaved", false);
            if (mUrlSaved)
            {
                mSavedUrl = savedInstanceState.getString("url");
                mUrlEditText.setText(mSavedUrl);
                Glide.with(this)
                        .load(mSavedUrl)
                        .error(R.drawable.error_circle_fail_failure_disallowed_x_cross_bad_svgrepo_com)
                        .listener(requestListener)
                        .into(mPlaceholderImage);
                saveIntent();
            }
        }

    }

    public void onClickFetch(View view)
    {
        String url = mUrlEditText.getText().toString().trim();
        // Check for two errors here, if the url box is empty, nothing to display
        // Also, if there is no internet, then a url cannot be accessed
        if (TextUtils.isEmpty(url)) {
            Toast.makeText(this, "Please enter a URL", Toast.LENGTH_SHORT).show();
            return;
        }

        if (!isInternetAvailable()) {
            Toast.makeText(this, "No internet connection. Please check your network and try again.", Toast.LENGTH_SHORT).show();
            return;
        }

        Glide.with(this)
                .load(url)
                .error(R.drawable.error_circle_fail_failure_disallowed_x_cross_bad_svgrepo_com)
                .listener(requestListener)
                .placeholder(R.drawable.ic_launcher_foreground)
                .into(mPlaceholderImage);

    }

    private boolean isInternetAvailable() {
        // Checks if there is either wifi or cellular data available to use on the current device
        ConnectivityManager connectivityManager = (ConnectivityManager) getSystemService(Context.CONNECTIVITY_SERVICE);
        if (connectivityManager != null) {
            NetworkCapabilities capabilities = connectivityManager.getNetworkCapabilities(connectivityManager.getActiveNetwork());
            return capabilities != null &&
                    (capabilities.hasTransport(NetworkCapabilities.TRANSPORT_WIFI) ||
                            capabilities.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR));
        }
        return false;
    }

    private void saveIntent()
    {
        Intent resultIntent = new Intent();
        resultIntent.putExtra("imageUrl", mSavedUrl);
        setResult(RESULT_OK, resultIntent);
    }

    public void onClickSaveImage(View view) {
        // If a fetch call was succesful, then it will save the image
        if (mUrlSaved) {
            saveIntent();
            Toast.makeText(this, "Image saved successfully.", Toast.LENGTH_SHORT).show();
        }
        else {
            Toast.makeText(this, "Cannot save, the previously entered URL is invalid or you haven't entered a URL", Toast.LENGTH_SHORT).show();
        }
    }

    public void onClickFinish(View view)
    {
        finish();
    }

    @Override
    protected void onSaveInstanceState(Bundle outState)
    {
        super.onSaveInstanceState(outState);
        outState.putBoolean("urlSaved", mUrlSaved);
        outState.putString("url", mSavedUrl);
    }
}
