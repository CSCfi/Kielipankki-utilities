<?xml version="1.0" encoding="UTF-8"?>

<!-- Produce fulltext HTML pages from the VRT files of the LA murre corpus. -->

<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns="http://www.w3.org/TR/xhtml1/strict">

  <xsl:output
      method="xml"
      omit-xml-declaration="yes"
      indent="yes"
      doctype-public="-//W3C//DTD XHTML 1.0 Strict//EN"
      doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"/>

  <xsl:template match="/text">
    <xsl:variable name="title">
      <xsl:value-of select="@parish_title"/>
      <xsl:text> (LA-murre) – kokoteksti</xsl:text>
    </xsl:variable>
<html>
  <head>
    <title><xsl:value-of select="$title"/></title>
    <link rel="stylesheet" type="text/css" href="la_murre_fulltext.css"/>
  </head>
  <body>
    <h1><xsl:value-of select="$title"/></h1>
    <table class="text-info">
      <tr>
	<td class="textinfo-name">Murrealue</td>
	<td class="textinfo-value">
	  <xsl:value-of select="@dialect_region_name"/>
	  <xsl:text> (</xsl:text>
	  <xsl:value-of select="@dialect_region"/>
	  <xsl:text>)</xsl:text>
	</td>
      </tr>
      <tr>
	<td class="textinfo-name">Murreryhmä</td>
	<td class="textinfo-value">
	  <xsl:value-of select="@dialect_group_name"/>
	  <xsl:text> (</xsl:text>
	  <xsl:value-of select="@dialect_group"/>
	  <xsl:text>)</xsl:text>
	</td>
      </tr>
      <tr>
	<td class="textinfo-name">Paikkakunta</td>
	<td class="textinfo-value"><xsl:value-of select="@parish"/></td>
      </tr>
      <tr>
	<td class="textinfo-name">Päiväys</td>
	<td class="textinfo-value"><xsl:value-of select="@date"/></td>
      </tr>
      <tr>
	<td class="textinfo-name">Kuvaus</td>
	<td class="textinfo-value"><xsl:value-of select="@session_descr"/></td>
      </tr>
      <tr>
	<td class="textinfo-name">Aihe</td>
	<td class="textinfo-value"><xsl:value-of select="@content_descr"/></td>
      </tr>
      <tr>
	<td class="textinfo-name">Projektin kuvaus</td>
	<td class="textinfo-value"><xsl:value-of select="@project_descr"/></td>
      </tr>
      <tr>
	<td class="textinfo-name">Tiedostonnimi</td>
	<td class="textinfo-value"><xsl:value-of select="@filename"/></td>
      </tr>
      <tr>
	<td class="textinfo-name">Alkuperäislähde</td>
	<td class="textinfo-value"><xsl:value-of select="@source_id"/></td>
      </tr>
    </table>
    <div class="text">
      <xsl:apply-templates select="paragraph"/>
    </div>
    <!-- The following URL requires a symlink from /var/www/html/korp
         to /var/www/html on the production server. -->
    <script language="javascript" type="text/javascript" src="/korp/fulltext/highlight_match.js"/>
  </body>
</html>
  </xsl:template>

  <xsl:template match="paragraph">
    <div class="turn-container {@type}" id="{@id}">
      <p class="turn-info">
	<xsl:text>[</xsl:text>
	<xsl:value-of select="@id"/>
	<xsl:text> </xsl:text>
	<xsl:value-of select="@type"/>
	<xsl:text> </xsl:text>
	<xsl:value-of select="@speaker"/>
	<xsl:text> | </xsl:text>
	<a class="annex-link" href="https://lat.csc.fi/ds/annex/runLoader?{@annex_link}" target="_blank">kuuntele vuoro</a>
	<xsl:text>]</xsl:text>
      </p>
      <div class="turn">
	<xsl:apply-templates select="sentence"/>
      </div>
    </div>
  </xsl:template>

  <xsl:template match="sentence">
    <p id="s{@num}" class="sentence">
      <span class="sentence-info">[s<xsl:value-of select="@num"/>]</span>
      <xsl:apply-templates select="*">
	<xsl:with-param name="sentnr" select="@num"/>
      </xsl:apply-templates>
    </p>
  </xsl:template>

  <xsl:template match="clause">
    <xsl:param name="sentnr"/>
    <span class="clause">
      <xsl:apply-templates select="token">
	<xsl:with-param name="sentnr" select="$sentnr"/>
      </xsl:apply-templates>
    </span>
  </xsl:template>

  <xsl:template match="token">
    <xsl:param name="sentnr"/>
    <span class="word" id="s{$sentnr}w{@num}"><xsl:value-of select="attr[1]/text()"></xsl:value-of></span><xsl:text> </xsl:text>
  </xsl:template>

</xsl:stylesheet>
