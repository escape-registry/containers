---
layout: default
title: Docker Environment Recipes Catalogue
---

# Docker Environment Recipes Catalogue

Welcome to the catalogue of available Docker container environments. Each environment below is defined by a `Dockerfile` and includes metadata for easy understanding and use.

## Available Environments

<input type="text" id="searchInput" onkeyup="filterEnvironments()" placeholder="Search for recipes by title, keyword, or author..." title="Type in a name">

<div id="environmentsList">
{% if site.data.environments and site.data.environments.size > 0 %}
  {% assign sorted_environments = site.data.environments | sort: "org.opencontainers.image.title" %}
  {% assign grouped_environments = sorted_environments | group_by: "_recipe_name" %}
  {% if grouped_environments %}
    {% for group in grouped_environments %}
      <h2>{{ group.name }}</h2>
      {% assign versions = group.items | sort: "org.escape-registry.recipe.version" | reverse %}
      <ul>
        {% for recipe in versions %}
          <li>
            <h3>
              {{ recipe['org.opencontainers.image.title'] | default: "Untitled" }}
              (Version: {{ recipe['org.escape-registry.recipe.version'] | default: "Unknown" }})
            </h3>
            <p><strong>Description:</strong> {{ recipe['org.opencontainers.image.description'] | default: "No description provided." }}</p>
            <p><strong>Author:</strong> {{ recipe['org.escape-registry.recipe.author'] | default: "N/A" }}</p>
            <p><strong>Keywords:</strong> 
              {% if recipe['org.escape-registry.recipe.keywords'] %}
                {% assign keywords = recipe['org.escape-registry.recipe.keywords'] | split: ',' %}
                {% for keyword in keywords %}
                  <span class="keyword">{{ keyword | strip }}</span>
                {% endfor %}
              {% else %}
                N/A
              {% endif %}
            </p>
            <p>
              <a href="{{ recipe['org.opencontainers.image.url'] }}" target="_blank" rel="noopener noreferrer">View Dockerfile on GitHub</a>
              {% if recipe['org.escape-registry.recipe.documentation'] and recipe['org.escape-registry.recipe.documentation'] != "" %}
                | <a href="{{ recipe['org.escape-registry.recipe.documentation'] }}" target="_blank" rel="noopener noreferrer">Recipe README</a>
              {% endif %}
            </p>
            <p><strong>Registry Image (Example):</strong> 
              `ghcr.io/{{ site.github.repository_owner | default: 'your-org' }}/{{ site.github.repository_name | default: 'your-repo' }}/{{ recipe['_recipe_name'] }}:{{ recipe['org.escape-registry.recipe.version'] | default: 'latest' }}`
            </p>
            {% if recipe['org.escape-registry.recipe.exposed_ports'] and recipe['org.escape-registry.recipe.exposed_ports'] != "" %}
              <p><strong>Exposed Ports:</strong> {{ recipe['org.escape-registry.recipe.exposed_ports'] }}</p>
            {% endif %}
            {% if recipe['org.escape-registry.recipe.build_arguments'] and recipe['org.escape-registry.recipe.build_arguments'] != "" %}
              <p><strong>Default Build Arguments:</strong> <code>{{ recipe['org.escape-registry.recipe.build_arguments'] }}</code></p>
            {% endif %}
          </li>
        {% endfor %}
      </ul>
    {% endfor %}
  {% else %}
    <p>No environments found. The `docs/_data/environments.json` file might be empty or missing. It is generated automatically by the CI/CD pipeline.</p>
  {% endif %}
{% else %}
  <p>No environments found. The `docs/_data/environments.json` file might be empty or missing. It is generated automatically by the CI/CD pipeline.</p>
{% endif %}
</div>

<style>
  body { font-family: sans-serif; line-height: 1.6; margin: 20px; }
  h1, h2, h3 { color: #333; }
  ul { list-style-type: none; padding-left: 0; }
  li { background-color: #f9f9f9; border: 1px solid #ddd; margin-bottom: 15px; padding: 15px; border-radius: 4px; }
  .keyword { background-color: #e0e0e0; padding: 2px 6px; border-radius: 3px; font-size: 0.9em; margin-right: 5px; }
  #searchInput { width: 100%; padding: 10px; margin-bottom: 20px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
</style>

<script>
function filterEnvironments() {
  var input, filter, ul, li, recipe, i, txtValue, title, keywords, author, recipeName;
  input = document.getElementById('searchInput');
  filter = input.value.toUpperCase();
  environmentsList = document.getElementById('environmentsList');
  // Get all h2 (recipe names) and their subsequent ul (versions)
  var recipeGroups = environmentsList.getElementsByTagName('h2');

  for (i = 0; i < recipeGroups.length; i++) {
    var recipeNameElement = recipeGroups[i];
    var versionList = recipeNameElement.nextElementSibling; // Assuming ul follows h2
    if (versionList && versionList.tagName === 'UL') {
      var versions = versionList.getElementsByTagName('li');
      var recipeGroupVisible = false;

      for (var j = 0; j < versions.length; j++) {
        recipe = versions[j];
        titleElement = recipe.getElementsByTagName('h3')[0];
        // Search in title, description, author, keywords
        var searchableText = recipe.textContent || recipe.innerText;

        if (searchableText.toUpperCase().indexOf(filter) > -1) {
          recipe.style.display = "";
          recipeGroupVisible = true;
        } else {
          recipe.style.display = "none";
        }
      }
      // Show/hide the recipe group title (h2)
      if (recipeGroupVisible) {
        recipeNameElement.style.display = "";
        versionList.style.display = "";
      } else {
        recipeNameElement.style.display = "none";
        versionList.style.display = "none";
      }
    }
  }
}
</script>