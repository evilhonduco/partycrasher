/**
 * Instantiate by dependency injection.
 *
 * function (PartyCrasher, $scope) { ... }
 */
angular.module('PartyCrasherApp')
.factory('PartyCrasher', function ($http, $httpParamSerializer) {
  class PartyCrasher {
    /**
     * Fetch a bucket by (project, threshold, id) tuple.
     * Pagination is optionally supported using from and size.
     *
     * Returns a Promise of the bucket data.
     */
    fetchBucket({project, threshold, id, from, size}) {
      if (!(project && threshold && id)) {
        return Promise.reject(new Error('Must provide project, threshold, and id'));
      }

      return $http.get(bucketURL({project, threshold, id, from, size}))
        .then(({data}) => data);
    }

    /**
     * Fetch a report by (project, id) pair.
     *
     * Returns a Promise of the report.
     */
    fetchReport({project, id}) {
      if (!(project && id)) {
        return Promise.reject(new Error('Must provide project and id'));
      }

      return $http.get(reportURL({ project, id }))
        .then(({data}) => data);
    }

    /**
     * Fetch a summary by (project, id) pair.
     *
     * Returns a Promise of the report.
     */
    fetchSummary({project, id}) {
      if (!(project && id)) {
        return Promise.reject(new Error('Must provide project and id'));
      }

      return $http.get(reportURL({ project, id }) + '/summary')
        .then(({data}) => data);
    }

    /**
     * Searches for buckets.
     * TODO: RENAME
     */
    search({ project, threshold, since, from, size }) {
      return $http.get(searchUrl({ project, threshold, since, from, size }))
        .then(({data}) => data);
    }

    searchQuery({ project, q, from, size }) {
      return $http.get(searchQueryUrl({ project, searchString: q, from, size }))
        .then(({data}) => data);
    }
  }

  function bucketURL({ project, threshold, id, from, size }) {
    var query = $httpParamSerializer({
      from: from || '0',
      size: size || '10'
    });
    return `/${project}/buckets/${threshold}/${id}?${query}`;
  }

  function reportURL({ project, id }) {
    /* Get rid of project prefix. */
    return `/${project}/reports/${id}`;
  }

  /* TODO: RENAME */
  function searchUrl({project, threshold, since, from, size}) {
    var query = $httpParamSerializer({
      since: since || '3-days-ago',
      from: from || '0',
      size: size || '10'
    });

    if (!project || project === '*') {
      /* Search ALL projects. */
      return `/buckets/${threshold}?${query}`;
    } else {
      /* Search just this project. */
      return `/${project}/buckets/${threshold}?${query}`;
    }
  }

  function searchQueryUrl({project, searchString, from, size}) {
    var query = $httpParamSerializer({
      searchString: searchString,
      from: from || '0',
      size: size || '10'
    });

    if (!project || project === '*') {
      /* Search ALL projects. */
      return `/*/search?${query}`;
    } else {
      /* Search just this project. */
      return `/${project}/search?${query}`;
    }
  }

  return new PartyCrasher();
});
