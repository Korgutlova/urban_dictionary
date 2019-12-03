function handleFileSelect(event) {
          var files = event.target.files; // FileList object
          // Loop through the FileList and render image files as thumbnails
          for (var i = 0, f; f = files[i]; i++) {
              // Only process image files
              if (!f.type.match('image.*')) continue;
              // Init FileReader()
              // See: https://developer.mozilla.org/en-US/docs/Web/API/FileReader
              var reader = new FileReader();
              // Closure to capture the file information
              reader.onload = (function () {
                  return function (e) {
                      // Render background image
                      document.getElementById('id_photo_preview').src = e.target.result;
                  };
              })(f);
              // Read in the image file as a data URL
              reader.readAsDataURL(f);
          }
      }

      // Change background after change file input
      // id_image — is default ID for ImageField input named `image` (in Django Admin)
      document.getElementById('id_photo').addEventListener('change', handleFileSelect, false);